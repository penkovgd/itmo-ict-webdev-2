from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .authors import Book


class BookGenreLink(SQLModel, table=True):
    book_id: int | None = Field(default=None, foreign_key="book.id", primary_key=True)
    genre_id: int | None = Field(default=None, foreign_key="genre.id", primary_key=True)


class GenreBase(SQLModel):
    name: str = Field(unique=True)


class Genre(GenreBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    books: list["Book"] = Relationship(
        back_populates="genres", link_model=BookGenreLink
    )


class GenrePublic(GenreBase):
    id: int


class GenreCreateUpdate(GenreBase):
    pass
