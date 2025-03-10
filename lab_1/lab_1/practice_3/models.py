from typing import List
from sqlmodel import SQLModel, Field, Relationship


class BookGenreLink(SQLModel, table=True):
    book_id: int = Field(default=None, foreign_key="book.id", primary_key=True)
    genre_id: int = Field(default=None, foreign_key="genre.id", primary_key=True)


class Genre(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    books: List["Book"] | None = Relationship(
        back_populates="genres", link_model=BookGenreLink
    )


class AuthorDefault(SQLModel):
    name: str
    surname: str
    country: str = ""


class Author(AuthorDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    author_books: List["Book"] | None = Relationship(back_populates="author")


class BookDefault(SQLModel):
    title: str
    author_id: int | None = Field(default=None, foreign_key="author.id")
    year: int
    description: str


class BookDetails(BookDefault):
    author: Author | None
    genres: List[Genre] | None


class BookCreate(BookDefault):
    genre_ids: List[int] | None


class Book(BookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    author: Author | None = Relationship(back_populates="author_books")
    genres: List[Genre] | None = Relationship(
        back_populates="books", link_model=BookGenreLink
    )
