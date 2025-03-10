from typing import List, TypedDict
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from lab_1.practice_3.models import (
    Author,
    Book,
    BookDefault,
    BookCreate,
    AuthorDefault,
    BookDetails,
    Genre,
)
from lab_1.practice_3.connection import init_db, get_session
from sqlmodel import select
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/books")
def read_books(session=Depends(get_session)) -> List[Book]:
    return session.exec(select(Book)).all()


@app.get("/books/{book_id}", response_model=BookDetails)
def read_book(book_id: int, session=Depends(get_session)) -> Book:
    return session.exec(select(Book).where(Book.id == book_id)).first()


@app.post("/books")
def create_book(book_data: BookCreate, session=Depends(get_session)) -> TypedDict(
    "Response", {"status": int, "data": Book}
):
    book = Book.model_validate(book_data)
    if book_data.genre_ids:
        genres = session.exec(
            select(Genre).where(Genre.id.in_(book_data.genre_ids))
        ).all()
        if len(genres) != len(book_data.genre_ids):
            raise HTTPException(status_code=404, detail="Genres not found")
        book.genres = genres
    session.add(book)
    session.commit()
    session.refresh(book)
    return {"status": 200, "data": book}


@app.delete("/books/{book_id}")
def delete_book(book_id: int, session=Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"status": 201, "message": "deleted"}


@app.patch("/books/{book_id}", response_model=BookDetails)
def update_book(
    book_id: int, book: BookCreate, session=Depends(get_session)
) -> BookDefault:
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = book.model_dump(exclude_unset=True)
    if "genre_ids" in book_data:
        genre_ids = book_data.pop("genre_ids")
        if genre_ids is not None:
            genres = session.exec(select(Genre).where(Genre.id.in_(genre_ids))).all()
            if len(genres) != len(genre_ids):
                raise HTTPException(status_code=404, detail="Genres not found")
            db_book.genres = genres
    for key, value in book_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/authors")
def read_authors(session=Depends(get_session)) -> List[Author]:
    return session.exec(select(Author)).all()


@app.get("/authors/{author_id}")
def read_author(author_id: int, session=Depends(get_session)) -> Author:
    return session.get(Author, author_id)


@app.post("/authors")
def create_author(author: AuthorDefault, session=Depends(get_session)) -> TypedDict(
    "Response", {"status": int, "data": Author}
):
    author = Author.model_validate(author)
    session.add(author)
    session.commit()
    session.refresh(author)
    return {"status": 200, "data": author}


@app.get("/genres")
def read_genres(session=Depends(get_session)) -> List[Genre]:
    return session.exec(select(Genre)).all()


@app.post("/genres")
def create_genre(genre: Genre, session=Depends(get_session)) -> Genre:
    genre = Genre.model_validate(genre)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
