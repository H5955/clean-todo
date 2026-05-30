from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

conn = sqlite3.connect("todos.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    completed INTEGER DEFAULT 0
)
""")

try:
    cursor.execute("ALTER TABLE todos ADD COLUMN completed INTEGER DEFAULT 0")
except:
    pass

conn.commit()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()

    completed_count = sum(todo[2] for todo in todos)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "todos": todos,
            "count": len(todos),
            "completed_count": completed_count
        }
    )


@app.post("/add")
async def add(task: str = Form(...)):

    cursor.execute(
        "INSERT INTO todos (task, completed) VALUES (?, ?)",
        (task, 0)
    )

    conn.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/toggle/{todo_id}")
async def toggle(todo_id: int):

    cursor.execute(
        "SELECT completed FROM todos WHERE id=?",
        (todo_id,)
    )

    row = cursor.fetchone()

    if row:
        new_value = 0 if row[0] else 1

        cursor.execute(
            "UPDATE todos SET completed=? WHERE id=?",
            (new_value, todo_id)
        )

        conn.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/delete/{todo_id}")
async def delete(todo_id: int):


    cursor.execute(
        "DELETE FROM todos WHERE id=?",
        (todo_id,)
    )

    conn.commit()

    return RedirectResponse("/", status_code=303)
