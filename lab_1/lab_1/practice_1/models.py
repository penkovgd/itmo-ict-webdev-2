from enum import Enum
from typing import List

from pydantic import BaseModel


class GenreEnum(Enum):
    dystopia = "Антиутопия"
    fiction = "Фантастика"
    classic = "Классика"
    mystic = "Мистика"


class Author(BaseModel):
    id: int
    name: str
    country: str


class Book(BaseModel):
    id: int
    title: str
    author: Author
    genres: List[GenreEnum]
    year: int
    description: str
