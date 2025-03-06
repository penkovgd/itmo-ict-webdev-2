from typing import List, TypedDict
from fastapi import FastAPI
from lab_1.practice_1.models import Author, Book

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/books")
def read_books() -> List[Book]:
    return temp_db


@app.get("/books/{book_id}")
def read_book(book_id: int) -> List[Book]:
    return [book for book in temp_db if book.get("id") == book_id]


@app.post("/books")
def create_book(book: Book) -> TypedDict("Response", {"status": int, "data": Book}):
    book_to_append = book.model_dump()
    temp_db.append(book_to_append)
    return {"status": 200, "data": book}


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(temp_db):
        if book.get("id") == book_id:
            temp_db.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book) -> List[Book]:
    for b in temp_db:
        if b.get("id") == book_id:
            book_to_append = book.model_dump()
            temp_db.remove(b)
            temp_db.append(book_to_append)
    return temp_db


@app.get("/authors")
def read_authors() -> List[Author]:
    return authors_db


@app.get("/authors/{author_id}")
def read_author(author_id: int) -> List[Author]:
    return [author for author in authors_db if author["id"] == author_id]


@app.post("/authors")
def create_author(author: Author) -> TypedDict(
    "Response", {"status": int, "data": Author}
):
    author_to_append = author.model_dump()
    authors_db.append(author_to_append)
    return {"status": 200, "data": author}


@app.delete("/authors/{author_id}")
def delete_author(author_id: int):
    for author in authors_db:
        if author["id"] == author_id:
            authors_db.remove(author)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/authors/{author_id}")
def update_author(author_id: int, author: Author) -> List[Author]:
    for a in authors_db:
        if a["id"] == author_id:
            author_to_append = author.model_dump()
            authors_db.remove(a)
            authors_db.append(author_to_append)
    return authors_db


temp_db = [
    {
        "id": 1,
        "title": "1984",
        "author": {
            "id": 1,
            "name": "Джордж Оруэлл",
            "country": "Великобритания",
        },
        "genres": ["Антиутопия", "Фантастика"],
        "year": 1949,
        "description": "Роман о тоталитарном обществе под постоянным контролем Большого Брата",
    },
    {
        "id": 2,
        "title": "Мастер и Маргарита",
        "author": {"id": 2, "name": "Михаил Булгаков", "country": "Россия"},
        "genres": ["Классика", "Фантастика"],
        "year": 1966,
        "description": "Мистическая сатира с дьяволом, философскими диалогами и вечной любовью",
    },
]

authors_db = [
    {
        "id": 1,
        "name": "Джордж Оруэлл",
        "country": "Великобритания",
    },
    {"id": 2, "name": "Михаил Булгаков", "country": "Россия"},
]
