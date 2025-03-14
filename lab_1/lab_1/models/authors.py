from sqlmodel import SQLModel, Field, Relationship
from pydantic_extra_types.country import CountryAlpha3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .books import Book, BookPublic


class AuthorBase(SQLModel):
    full_name: str
    country: CountryAlpha3 | None = (
        None  # Country code in ISO 3166-1 alpha-3 format (https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)
    )


class Author(AuthorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    books: list["Book"] = Relationship(back_populates="author")


class AuthorPublic(AuthorBase):
    id: int


class AuthorPublicWithBooks(AuthorPublic):
    books: list["BookPublic"] = []


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(SQLModel):
    full_name: str | None = None
    country: CountryAlpha3 | None = None


from .books import BookPublic

AuthorPublicWithBooks.model_rebuild()
