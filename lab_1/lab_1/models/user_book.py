# from sqlmodel import Field, SQLModel, Relationship
# from typing import TYPE_CHECKING, Optional

# if TYPE_CHECKING:
#     from .users import User
#     from .books import Book, BookPublicWithAuthorAndGenres


# class UserBookLinkPublic(SQLModel):
#     id: int
#     book_id: int
#     user_id: int


# class UserBookLinkPublicWithBook(UserBookLinkPublic):
#     book: "BookPublicWithAuthorAndGenres"


# from .books import BookPublicWithAuthorAndGenres

# UserBookLinkPublicWithBook.model_rebuild()
