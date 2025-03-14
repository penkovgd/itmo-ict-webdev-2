from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from .books import BookPublic, Book

if TYPE_CHECKING:
    from .users import User, UserPublic


class SwapStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"


class SwapRespondEnum(str, Enum):
    ACCEPT = "accept"
    DENY = "deny"


class Swap(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: SwapStatusEnum = SwapStatusEnum.PENDING

    initiator_user_id: int | None = Field(default=None, foreign_key="user.id")
    initiator_book_id: int | None = Field(default=None, foreign_key="book.id")

    responder_user_id: int | None = Field(default=None, foreign_key="user.id")
    responder_book_id: int | None = Field(default=None, foreign_key="book.id")

    initiator_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Swap.initiator_user_id"}
    )
    responder_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Swap.responder_user_id"}
    )
    initiator_book: "Book" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Swap.initiator_book_id"}
    )
    responder_book: "Book" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Swap.responder_book_id"}
    )

    # initiator_userbooklink_id: int | None = Field(
    #     default=None, foreign_key="userbooklink.id"
    # )
    # responder_userbooklink_id: int | None = Field(
    #     default=None, foreign_key="userbooklink.id"
    # )

    # initiator_userbooklink: "UserBookLink" = Relationship(
    #     sa_relationship_kwargs={"foreign_keys": "Swap.initiator_userbooklink_id"}
    # )
    # responder_userbooklink: "UserBookLink" = Relationship(
    #     sa_relationship_kwargs={"foreign_keys": "Swap.responder_userbooklink_id"}
    # )


class SwapPublic(SQLModel):
    id: int
    status: SwapStatusEnum = SwapStatusEnum.PENDING
    initiator_user: "UserPublic"
    initiator_book: "BookPublic"

    responder_user: "UserPublic"
    responder_book: "BookPublic"


class SwapCreate(SQLModel):
    responder_user_id: int  # кому предлагаем обмен
    initiator_book_id: int  # какую книгу мы предлагаем
    responder_book_id: int  # какую книгу responder'а хотим взамен


from .users import UserPublic
from .books import BookPublic

SwapPublic.model_rebuild()
