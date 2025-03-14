from typing import Annotated
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from passlib.context import CryptContext
import jwt

from dotenv import load_dotenv
from os import getenv

from lab_1.connection import get_session
from lab_1.models.users import User, UserCreate, UserPublic, UserLogin

load_dotenv()
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"])


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_token(payload: dict):
    to_encode = payload.copy()
    expire = datetime.now(timezone(timedelta(hours=3))) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload["sub"]
        return sub
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired signature")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)],
):
    email = decode_token(credentials.credentials)
    current_user = session.exec(select(User).where(User.email == email)).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    return current_user


@router.post("/register", response_model=UserPublic)
def register(user: UserCreate, session: Annotated[Session, Depends(get_session)]):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User.model_validate(user, update={"hashed_password": hashed_password})
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login")
def login(user: UserLogin, session: Annotated[Session, Depends(get_session)]):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="User with this email not found")
    password_is_valid = verify_password(user.password, db_user.hashed_password)
    if not password_is_valid:
        raise HTTPException(status_code=401, detail="Wrong password")
    token = create_token({"sub": db_user.email})
    return {"token": token}
