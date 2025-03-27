# Лабораторная работа 1. Реализация серверного приложения FastAPI

Выбранный вариант:

??? note "Разработка веб-приложения для буккросинга"
    Ваша задача - создать веб-приложение, которое позволит пользователям обмениваться книгами между собой. Это приложение должно облегчать процесс обмена книгами, позволяя пользователям находить книги, которые им интересны, и находить новых пользователей для обмена книгами. Функционал веб-приложения должен включать следующее:

    - Создание профилей: Возможность пользователям создавать профили, указывать информацию о себе, своих навыках, опыте работы и предпочтениях по проектам.

    - Добавление книг в библиотеку: Пользователи могут добавлять книги, которыми они готовы поделиться, в свою виртуальную библиотеку на платформе.

    - Поиск и запросы на обмен: Функционал поиска книг в библиотеке других пользователей. Возможность отправлять запросы на обмен книгами другим пользователям.

    - Управление запросами и обменами: Возможность просмотра и управления запросами на обмен. Возможность подтверждения или отклонения запросов на обмен.

[github Лабораторной работы 1](https://github.com/penkovgd/itmo-ict-webdev-2/tree/lab_1)

Практические работы:

- [Практическая работа 1](https://github.com/penkovgd/itmo-ict-webdev-2/tree/lab_1/lab_1/lab_1/practice_1)
- [Практическая работа 2](https://github.com/penkovgd/itmo-ict-webdev-2/tree/lab_1/lab_1/lab_1/practice_2)
- [Практическая работа 3](https://github.com/penkovgd/itmo-ict-webdev-2/tree/lab_1/lab_1/lab_1/practice_3)

Примеры кода:

??? note "CRUD-ы модели Book"
    ```python
    router = APIRouter(prefix="/books", tags=["books"])


    @router.get("/", response_model=list[BookPublicWithAuthorAndGenres])
    def read_books(
        session: Session = Depends(get_session),
        genre_id: int | None = None,
        author_id: int | None = None,
    ):
        query = select(Book)

        if author_id is not None:
            query = query.where(Book.author_id == author_id)

        if genre_id is not None:
            query = query.join(Book.genres).where(Genre.id == genre_id).distinct()

        books = session.exec(query).all()
        return books


    @router.get(
        "/{book_id}",
        response_model=BookPublicWithAuthorAndGenres,
    )
    def read_book(book_id: int, session: Session = Depends(get_session)):
        db_book = session.get(Book, book_id)
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")
        return db_book


    @router.post("/", response_model=BookPublicWithAuthorAndGenres)
    def create_books(book: BookCreate, session: Session = Depends(get_session)):
        author = session.get(Author, book.author_id)
        if not author:
            raise HTTPException(status_code=400, detail="Author not found")
        db_book = Book.model_validate(book)
        for genre_id in book.genre_ids:
            genre = session.get(Genre, genre_id)
            if not genre:
                raise HTTPException(
                    status_code=404, detail=f"Genre with id '{genre_id}' not found"
                )
            db_book.genres.append(genre)
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book


    @router.patch("/{book_id}", response_model=BookPublicWithAuthorAndGenres)
    def update_book(
        book_id: int, book: BookUpdate, session: Session = Depends(get_session)
    ):
        db_book = session.get(Book, book_id)
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")

        book_data = book.model_dump(exclude_unset=True)
        if "author_id" in book_data:
            author = session.get(Author, book_data["author_id"])
            if not author:
                raise HTTPException(status_code=400, detail="Author not found")
        if "genre_ids" in book_data:
            new_genres = []
            for genre_id in book_data["genre_ids"]:
                genre = session.get(Genre, genre_id)
                if not genre:
                    raise HTTPException(
                        status_code=404, detail=f"Genre with id '{genre_id}' not found"
                    )
                new_genres.append(genre)
            db_book.genres = new_genres
        db_book.sqlmodel_update(book_data)
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book


    @router.delete("/{book_id}")
    def delete_book(book_id: int, session: Session = Depends(get_session)):
        db_book = session.get(Book, book_id)
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(db_book)
        session.commit()
        return {"status": 201, "message": "deleted"}

    ```

??? note "JWT-аутентификация"
    ```python
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

    ```

??? note "Обмены книгами (swaps)"
    ```python
    router = APIRouter(prefix="/swaps", tags=["swaps"])


    @router.get("/my", response_model=list[SwapPublic])
    def read_my_swaps(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
        user_role: Literal["initiator", "responder"] | None = None,
        status: SwapStatusEnum | None = None,
    ):
        query = select(Swap)

        if user_role == "initiator":
            query = query.where(Swap.initiator_user_id == current_user.id)
        elif user_role == "responder":
            query = query.where(Swap.responder_user_id == current_user.id)
        else:
            query = query.where(
                or_(
                    Swap.initiator_user_id == current_user.id,
                    Swap.responder_user_id == current_user.id,
                )
            )
        if status:
            query = query.where(Swap.status == status)

        my_swaps = session.exec(query).all()
        return my_swaps


    def is_user_book_in_active_swaps(session: Session, user_id: int, book_id: int) -> bool:
        """Проверяет, участвует ли книга пользователя в его активных обменах."""
        return (
            session.exec(
                select(Swap).where(
                    or_(  # Либо:
                        and_(  # user уже предлагает данную книгу в другом обмене (этот обмен он сам инициировал)
                            Swap.initiator_user_id == user_id,
                            Swap.initiator_book_id == book_id,
                        ),
                        and_(  # user может отдать данную книгу в другом обмене (на этот обмен он отвечает)
                            Swap.responder_user_id == user_id,
                            Swap.responder_book_id == book_id,
                        ),
                    ),  # Актуально только для активных обменов
                    Swap.status == SwapStatusEnum.PENDING,
                )
            ).first()
            is not None
        )


    @router.post("/", response_model=SwapPublic)
    def create_swap(
        swap_create: SwapCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
    ):
        responder = session.get(User, swap_create.responder_user_id)
        initiator_book = session.get(Book, swap_create.initiator_book_id)
        responder_book = session.get(Book, swap_create.responder_book_id)

        # Провка на наличие человека, с каоторым проводим обмен, и наличие книг в бд:
        if not responder:
            raise HTTPException(status_code=404, detail="Responder not found")
        if not initiator_book:
            raise HTTPException(
                status_code=404,
                detail=f"Boot with id {swap_create.initiator_book_id} not found",
            )
        if not responder_book:
            raise HTTPException(
                status_code=404,
                detail=f"Boot with id {swap_create.responder_book_id} not found",
            )

        # Проверям, действительно ли пользователи владеют указанными книгами:
        if responder_book not in responder.books:
            raise HTTPException(
                status_code=400,
                detail=f"Responder doesn't have book with id {responder_book.id}",
            )
        if initiator_book not in current_user.books:
            raise HTTPException(
                status_code=400, detail=f"You don't have book with id {initiator_book.id}"
            )

        # Проверяем, есть ли такой же активный обмен (PENDING).
        existing_pending_swap = session.exec(
            select(Swap)
            .where(Swap.initiator_user_id == current_user.id)
            .where(Swap.responder_user_id == responder.id)
            .where(Swap.initiator_book_id == initiator_book.id)
            .where(Swap.responder_book_id == responder_book.id)
            .where(Swap.status == SwapStatusEnum.PENDING)
        ).first()
        if existing_pending_swap:
            raise HTTPException(status_code=400, detail="Same pending swap already exists")

        # Так же нельзя создать обмен на книги, которые уже участвуют в активном обмене (они как бы заморожены):
        if is_user_book_in_active_swaps(session, current_user.id, initiator_book.id):
            raise HTTPException(
                status_code=400,
                detail="Your book is already participating in another of your swaps",
            )
        if is_user_book_in_active_swaps(session, responder.id, responder_book.id):
            raise HTTPException(
                status_code=400,
                detail="The book you want to get is already participating in another responder's swap",
            )

        # Теперь можно создать обмен:
        db_swap = Swap(
            initiator_user_id=current_user.id,
            initiator_book_id=initiator_book.id,
            responder_user_id=responder.id,
            responder_book_id=responder_book.id,
        )
        session.add(db_swap)
        session.commit()
        session.refresh(db_swap)
        return db_swap


    @router.patch("/{swap_id}/respond", response_model=SwapPublic)
    def respond_to_swap(
        swap_id: int,
        respond: SwapRespondEnum,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
    ):
        db_swap = session.get(Swap, swap_id)
        if not db_swap:
            raise HTTPException(status_code=404, detail="Swap not found")

        # мы можем ответить на обмен только если мы ответчики (responder):
        if db_swap.responder_user_id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="You can't respond to swap, because you are not a responder",
            )
        # мы также не можем ответить на неактуальный обмен:
        if db_swap.status != SwapStatusEnum.PENDING:
            raise HTTPException(
                status_code=400, detail="You can't respont to swap which isn't pending"
            )

        if respond == SwapRespondEnum.ACCEPT:
            initiator = db_swap.initiator_user
            initiator.books.append(db_swap.responder_book)
            initiator.books.remove(db_swap.initiator_book)

            current_user.books.append(db_swap.initiator_book)
            current_user.books.remove(db_swap.responder_book)

            db_swap.status = SwapStatusEnum.COMPLETED

            session.add(db_swap)
            session.add(initiator)
            session.add(current_user)
            session.commit()
            session.refresh(db_swap)

        if respond == SwapRespondEnum.DENY:
            db_swap.status = SwapStatusEnum.CANCELED
            session.add(db_swap)
            session.commit()
            session.refresh(db_swap)

        return db_swap

    ```
