from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from lab_1.connection import get_session
from lab_1.models.authors import (
    Author,
    AuthorCreate,
    AuthorPublic,
    AuthorPublicWithBooks,
    AuthorUpdate,
)

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=list[AuthorPublicWithBooks])
def read_authors(session: Session = Depends(get_session)):
    authors = session.exec(select(Author)).all()
    return authors


@router.get("/{author_id}", response_model=AuthorPublicWithBooks)
def read_author(author_id: int, session: Session = Depends(get_session)):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post("/", response_model=AuthorPublic)
def create_author(author: AuthorCreate, session: Session = Depends(get_session)):
    db_author = Author.model_validate(author)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author


@router.patch("/{author_id}", response_model=AuthorPublic)
def update_author(
    author_id: int, author: AuthorUpdate, session: Session = Depends(get_session)
):
    db_author = session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    author_data = author.model_dump(exclude_unset=True)
    db_author.sqlmodel_update(author_data)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author


@router.delete("/{author_id}")
def delete_author(author_id: int, session: Session = Depends(get_session)):
    db_author = session.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    session.delete(db_author)
    session.commit()
    return {"status": 201, "message": "deleted"}
