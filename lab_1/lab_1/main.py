from fastapi import FastAPI
import uvicorn
from lab_1.connection import init_db
from lab_1.routers import books, authors, genres, auth, users, swaps


app = FastAPI()
app.include_router(books.router)
app.include_router(authors.router)
app.include_router(genres.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(swaps.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
