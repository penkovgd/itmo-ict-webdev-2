from typing import TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .books import Book, BookPublic


class UserBookLink(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int | None = Field(default=None, foreign_key="book.id")
    user_id: int | None = Field(default=None, foreign_key="user.id")

    book: "Book" = Relationship()
    user: "User" = Relationship()


class UserBookLinkPublic(SQLModel):
    id: int
    book_id: int
    user_id: int


class UserBookLinkPublicWithUserAndBook(SQLModel):
    id: int
    book: "BookPublic"
    user: "UserPublic"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)
    full_name: str
    bio: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    books: list["Book"] = Relationship(back_populates="users", link_model=UserBookLink)


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    full_name: str | None = None
    bio: str | None = None
    password: str | None = Field(min_length=6, default=None)


class UserLogin(SQLModel):
    email: EmailStr
    password: str = Field(min_length=6)
