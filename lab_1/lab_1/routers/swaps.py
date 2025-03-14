from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, or_, and_
from lab_1.connection import get_session
from lab_1.models.users import User
from lab_1.models.books import Book
from lab_1.models.swaps import (
    Swap,
    SwapCreate,
    SwapPublic,
    SwapStatusEnum,
    SwapRespondEnum,
)
from lab_1.routers.auth import get_current_user

router = APIRouter(prefix="/swaps", tags=["swaps"])


@router.get("/my", response_model=list[SwapPublic])
def read_my_swaps(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    user_role: Literal["initiator", "responder"] | None = None,
    status: SwapStatusEnum | None = None,
):
    query = select(Swap)

    if user_role == "initiator":
        query = query.where(Swap.initiator_user_id == current_user.id)
    elif user_role == "responder":
        query = query.where(Swap.responder_user_id == current_user.id)
    else:
        query = query.where(
            or_(
                Swap.initiator_user_id == current_user.id,
                Swap.responder_user_id == current_user.id,
            )
        )
    if status:
        query = query.where(Swap.status == status)

    my_swaps = session.exec(query).all()
    return my_swaps


def is_user_book_in_active_swaps(session: Session, user_id: int, book_id: int) -> bool:
    """Проверяет, участвует ли книга пользователя в его активных обменах."""
    return (
        session.exec(
            select(Swap).where(
                or_(  # Либо:
                    and_(  # user уже предлагает данную книгу в другом обмене (этот обмен он сам инициировал)
                        Swap.initiator_user_id == user_id,
                        Swap.initiator_book_id == book_id,
                    ),
                    and_(  # user может отдать данную книгу в другом обмене (на этот обмен он отвечает)
                        Swap.responder_user_id == user_id,
                        Swap.responder_book_id == book_id,
                    ),
                ),  # Актуально только для активных обменов
                Swap.status == SwapStatusEnum.PENDING,
            )
        ).first()
        is not None
    )


@router.post("/", response_model=SwapPublic)
def create_swap(
    swap_create: SwapCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    responder = session.get(User, swap_create.responder_user_id)
    initiator_book = session.get(Book, swap_create.initiator_book_id)
    responder_book = session.get(Book, swap_create.responder_book_id)

    # Провка на наличие человека, с каоторым проводим обмен, и наличие книг в бд:
    if not responder:
        raise HTTPException(status_code=404, detail="Responder not found")
    if not initiator_book:
        raise HTTPException(
            status_code=404,
            detail=f"Boot with id {swap_create.initiator_book_id} not found",
        )
    if not responder_book:
        raise HTTPException(
            status_code=404,
            detail=f"Boot with id {swap_create.responder_book_id} not found",
        )

    # Проверям, действительно ли пользователи владеют указанными книгами:
    if responder_book not in responder.books:
        raise HTTPException(
            status_code=400,
            detail=f"Responder doesn't have book with id {responder_book.id}",
        )
    if initiator_book not in current_user.books:
        raise HTTPException(
            status_code=400, detail=f"You don't have book with id {initiator_book.id}"
        )

    # Проверяем, есть ли такой же активный обмен (PENDING).
    existing_pending_swap = session.exec(
        select(Swap)
        .where(Swap.initiator_user_id == current_user.id)
        .where(Swap.responder_user_id == responder.id)
        .where(Swap.initiator_book_id == initiator_book.id)
        .where(Swap.responder_book_id == responder_book.id)
        .where(Swap.status == SwapStatusEnum.PENDING)
    ).first()
    if existing_pending_swap:
        raise HTTPException(status_code=400, detail="Same pending swap already exists")

    # Так же нельзя создать обмен на книги, которые уже участвуют в активном обмене (они как бы заморожены):
    if is_user_book_in_active_swaps(session, current_user.id, initiator_book.id):
        raise HTTPException(
            status_code=400,
            detail="Your book is already participating in another of your swaps",
        )
    if is_user_book_in_active_swaps(session, responder.id, responder_book.id):
        raise HTTPException(
            status_code=400,
            detail="The book you want to get is already participating in another responder's swap",
        )

    # Теперь можно создать обмен:
    db_swap = Swap(
        initiator_user_id=current_user.id,
        initiator_book_id=initiator_book.id,
        responder_user_id=responder.id,
        responder_book_id=responder_book.id,
    )
    session.add(db_swap)
    session.commit()
    session.refresh(db_swap)
    return db_swap


@router.patch("/{swap_id}/respond", response_model=SwapPublic)
def respond_to_swap(
    swap_id: int,
    respond: SwapRespondEnum,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_swap = session.get(Swap, swap_id)
    if not db_swap:
        raise HTTPException(status_code=404, detail="Swap not found")

    # мы можем ответить на обмен только если мы ответчики (responder):
    if db_swap.responder_user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You can't respond to swap, because you are not a responder",
        )
    # мы также не можем ответить на неактуальный обмен:
    if db_swap.status != SwapStatusEnum.PENDING:
        raise HTTPException(
            status_code=400, detail="You can't respont to swap which isn't pending"
        )

    if respond == SwapRespondEnum.ACCEPT:
        initiator = db_swap.initiator_user
        initiator.books.append(db_swap.responder_book)
        initiator.books.remove(db_swap.initiator_book)

        current_user.books.append(db_swap.initiator_book)
        current_user.books.remove(db_swap.responder_book)

        db_swap.status = SwapStatusEnum.COMPLETED

        session.add(db_swap)
        session.add(initiator)
        session.add(current_user)
        session.commit()
        session.refresh(db_swap)

    if respond == SwapRespondEnum.DENY:
        db_swap.status = SwapStatusEnum.CANCELED
        session.add(db_swap)
        session.commit()
        session.refresh(db_swap)

    return db_swap
