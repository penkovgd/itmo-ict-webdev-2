from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from lab_1.connection import get_session
from lab_1.models.books import (
    Book,
    BookPublic,
    BookPublicWithAuthorAndGenres,
    BookCreate,
    BookUpdate,
)
from lab_1.models.authors import Author
from lab_1.models.genres import Genre

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookPublicWithAuthorAndGenres])
def read_books(
    session: Session = Depends(get_session),
    genre_id: int | None = None,
    author_id: int | None = None,
):
    query = select(Book)

    if author_id is not None:
        query = query.where(Book.author_id == author_id)

    if genre_id is not None:
        query = query.join(Book.genres).where(Genre.id == genre_id).distinct()

    books = session.exec(query).all()
    return books


@router.get(
    "/{book_id}",
    response_model=BookPublicWithAuthorAndGenres,
)
def read_book(book_id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.post("/", response_model=BookPublicWithAuthorAndGenres)
def create_books(book: BookCreate, session: Session = Depends(get_session)):
    author = session.get(Author, book.author_id)
    if not author:
        raise HTTPException(status_code=400, detail="Author not found")
    db_book = Book.model_validate(book)
    for genre_id in book.genre_ids:
        genre = session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(
                status_code=404, detail=f"Genre with id '{genre_id}' not found"
            )
        db_book.genres.routerend(genre)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.patch("/{book_id}", response_model=BookPublicWithAuthorAndGenres)
def update_book(
    book_id: int, book: BookUpdate, session: Session = Depends(get_session)
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = book.model_dump(exclude_unset=True)
    if "author_id" in book_data:
        author = session.get(Author, book_data["author_id"])
        if not author:
            raise HTTPException(status_code=400, detail="Author not found")
    if "genre_ids" in book_data:
        new_genres = []
        for genre_id in book_data["genre_ids"]:
            genre = session.get(Genre, genre_id)
            if not genre:
                raise HTTPException(
                    status_code=404, detail=f"Genre with id '{genre_id}' not found"
                )
            new_genres.append(genre)
        db_book.genres = new_genres
    db_book.sqlmodel_update(book_data)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(db_book)
    session.commit()
    return {"status": 201, "message": "deleted"}
