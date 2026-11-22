# library_management2


FastAPI + raw PostgreSQL (psycopg, no ORM) se bana Library CRUD project.

## Setup
1. `python -m venv venv` aur `venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `.env.example` ko copy karke `.env` banao aur apna password daalo
4. PostgreSQL mein database banao aur `schema.sql` chalao
5. `python -m uvicorn main:app --reload`

## Endpoints
| Method | URL | Kaam |
|--------|-----|------|
| POST | /books | Nayi book |
| GET | /books | Saari books (limit, offset) |
| GET | /books/{id} | Ek book |
| PUT | /books/{id} | Poora update |
| PATCH | /books/{id} | Thoda update |
| DELETE | /books/{id} | Delete |

Docs: http://127.0.0.1:8000/docs