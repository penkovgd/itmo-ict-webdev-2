from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from lab_1.connection import get_session
from lab_1.models.genres import Genre, GenreCreateUpdate, GenrePublic

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=list[GenrePublic])
def read_genres(session: Session = Depends(get_session)):
    genres = session.exec(select(Genre)).all()
    return genres


@router.get("/{genre_id}", response_model=GenrePublic)
def read_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("/", response_model=GenrePublic)
def create_genre(genre: GenreCreateUpdate, session: Session = Depends(get_session)):
    existing_genre = session.exec(select(Genre).where(Genre.name == genre.name)).first()
    if existing_genre:
        raise HTTPException(
            status_code=400, detail=f"Genre '{genre.name}' already exists"
        )
    db_genre = Genre.model_validate(genre)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@router.patch("/{genre_id}", response_model=GenrePublic)
def update_genre(
    genre_id: int, genre: GenreCreateUpdate, session: Session = Depends(get_session)
):
    existing_genre = session.exec(select(Genre).where(Genre.name == genre.name)).first()
    if existing_genre:
        raise HTTPException(
            status_code=400, detail=f"Genre '{genre.name}' already exists"
        )
    db_genre = session.get(Genre, genre_id)
    if not db_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    genre_data = genre.model_dump(exclude_unset=True)
    db_genre.sqlmodel_update(genre_data)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@router.delete("/{genre_id}")
def delete_genre(genre_id: int, session: Session = Depends(get_session)):
    db_genre = session.get(Genre, genre_id)
    if not db_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    session.delete(db_genre)
    session.commit()
    return {"status": 201, "message": "deleted"}
