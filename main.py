from typing import Optional
import psycopg
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from database import get_connection

app = FastAPI(title="Library Management API")


@app.exception_handler(psycopg.Error)
def database_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Database error, try again later"})


class Book(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=150)
    author: str = Field(min_length=1, max_length=100)
    published_year: int = Field(ge=1000, le=2100)
    copies: int = Field(ge=0)


class BookPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    published_year: Optional[int] = Field(default=None, ge=1000, le=2100)
    copies: Optional[int] = Field(default=None, ge=0)


@app.get("/books")
def get_books(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM books ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
        return cur.fetchall()


@app.get("/books/{book_id}")
def get_book(book_id: int = Path(gt=0)):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return row


@app.post("/books", status_code=201)
def create_book(book: Book):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO books (title, author, published_year, copies) "
            "VALUES (%s, %s, %s, %s) RETURNING *",
            (book.title, book.author, book.published_year, book.copies),
        )
        return cur.fetchone()


@app.put("/books/{book_id}")
def update_book(book: Book, book_id: int = Path(gt=0)):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE books SET title = %s, author = %s, published_year = %s, copies = %s "
            "WHERE id = %s",
            (book.title, book.author, book.published_year, book.copies, book_id),
        )
        updated = cur.rowcount
    if updated == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated"}


@app.patch("/books/{book_id}")
def patch_book(book: BookPatch, book_id: int = Path(gt=0)):
    if not book.model_dump(exclude_none=True):
        raise HTTPException(status_code=400, detail="Kam se kam ek field bhejo")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE books SET "
            "title = COALESCE(%s, title), "
            "author = COALESCE(%s, author), "
            "published_year = COALESCE(%s, published_year), "
            "copies = COALESCE(%s, copies) "
            "WHERE id = %s",
            (book.title, book.author, book.published_year, book.copies, book_id),
        )
        updated = cur.rowcount
    if updated == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated"}


@app.delete("/books/{book_id}")
def delete_book(book_id: int = Path(gt=0)):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        deleted = cur.rowcount
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}