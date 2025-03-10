from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()


db_url = f"postgresql+psycopg2://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@localhost/books_practice_2"
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
