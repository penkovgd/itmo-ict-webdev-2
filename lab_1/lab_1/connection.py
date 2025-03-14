from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
from os import getenv
from typing import Iterator

load_dotenv()

db_url = getenv("DB_BOOKS_URL")
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
