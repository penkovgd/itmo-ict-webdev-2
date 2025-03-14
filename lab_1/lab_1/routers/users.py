from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from lab_1.connection import get_session
from lab_1.models.users import (
    User,
    UserPublic,
    UserUpdate,
)
from lab_1.models.books import Book, BookPublic, BookPublicWithAuthorAndGenres
from lab_1.routers.auth import get_current_user, get_password_hash
from lab_1.routers.swaps import is_user_book_in_active_swaps

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserPublic])
def read_users(session: Annotated[Session, Depends(get_session)]):
    users = session.exec(select(User)).all()
    return users


@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_current_user(
    user: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    user_data = user.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        hashed_password = get_password_hash(user_data["password"])
        extra_data["hashed_password"] = hashed_password
    if "email" in user_data:
        existing_email = session.exec(
            select(User).where(User.email == user_data["email"])
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )
    current_user.sqlmodel_update(user_data, update=extra_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/me/books", response_model=list[BookPublicWithAuthorAndGenres])
def read_current_user_books(
    current_user: Annotated[User, Depends(get_current_user)],
):
    books = current_user.books
    return books


@router.get("/{user_id}/books", response_model=list[BookPublicWithAuthorAndGenres])
def read_user_books(user_id: int, session: Annotated[Session, Depends(get_session)]):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    books = db_user.books
    return books


@router.post("/me/books", response_model=list[BookPublicWithAuthorAndGenres])
def add_book_to_current_user(
    book_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if db_book in current_user.books:
        raise HTTPException(
            status_code=400, detail="Book is alredy own by current user"
        )
    current_user.books.append(db_book)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user.books


@router.delete("/me/books/{book_id}")
def remove_book_from_current_user(
    book_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if db_book not in current_user.books:
        raise HTTPException(
            status_code=400, detail="Current user doesn't own this book"
        )
    # Нельзя удалить книгу, которая участвует в обменах. Она как бы заморожена
    if is_user_book_in_active_swaps(
        session, user_id=current_user.id, book_id=db_book.id
    ):
        raise HTTPException(
            status_code=400,
            detail="You cannot delete a book that is participating in your active swaps",
        )
    current_user.books.remove(db_book)
    session.add(current_user)
    session.commit()
    return {"status": 201, "message": "deleted"}
