from sqlmodel import SQLModel, Field, Relationship
from pydantic import PositiveInt
from typing import TYPE_CHECKING, Optional

from .genres import Genre, BookGenreLink
from .users import User, UserBookLink

if TYPE_CHECKING:
    from .authors import Author, AuthorPublic


class BookBase(SQLModel):
    title: str
    year: PositiveInt | None = None
    description: str | None = None

    author_id: int | None = Field(default=None, foreign_key="author.id")


class Book(BookBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    author: Optional["Author"] = Relationship(back_populates="books")

    genres: list[Genre] = Relationship(back_populates="books", link_model=BookGenreLink)
    users: list[User] = Relationship(back_populates="books", link_model=UserBookLink)


class BookPublic(BookBase):
    id: int


class BookPublicWithAuthorAndGenres(BookPublic):
    author: Optional["AuthorPublic"] = None
    genres: list[Genre] = []


class BookCreate(BookBase):
    genre_ids: list[int] = []


class BookUpdate(SQLModel):
    title: str | None = None
    year: PositiveInt | None = None
    description: str | None = None
    author_id: int | None = None
    genre_ids: list[int] = []


from .authors import AuthorPublic

BookPublicWithAuthorAndGenres.model_rebuild()
