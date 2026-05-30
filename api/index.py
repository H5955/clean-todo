from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg.connect(DATABASE_URL)
cursor = conn.cursor()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

cursor.execute("""
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    task TEXT,
    completed INTEGER DEFAULT 0
)
""")

conn.commit()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    todos = cursor.fetchall()

    completed_count = sum(todo[2] for todo in todos)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "todos": todos,
            "count": len(todos),
            "completed_count": completed_count
        }
    )


@app.post("/add")
async def add(task: str = Form(...)):
    cursor.execute(
        "INSERT INTO todos (task, completed) VALUES (%s, %s)",
        (task, 0)
    )

    conn.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/toggle/{todo_id}")
async def toggle(todo_id: int):
    cursor.execute(
        "SELECT completed FROM todos WHERE id=%s",
        (todo_id,)
    )

    row = cursor.fetchone()

    if row:
        new_value = 0 if row[0] else 1

        cursor.execute(
            "UPDATE todos SET completed=%s WHERE id=%s",
            (new_value, todo_id)
        )

        conn.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/delete/{todo_id}")
async def delete(todo_id: int):
    cursor.execute(
        "DELETE FROM todos WHERE id=%s",
        (todo_id,)
    )

    conn.commit()

    return RedirectResponse("/", status_code=303)
