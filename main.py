import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    description="A small to-do list API backed by SQLite (tasks.db) — data survives restarts.",
    version="1.0",
)


class Task(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


DB_PATH = Path(__file__).parent / "tasks.db"

SEED_TASKS = [
    ("Buy milk", 0),
    ("Walk the dog", 0),
    ("Read a book", 1),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        with conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS tasks ("
                "id INTEGER PRIMARY KEY, "
                "title TEXT NOT NULL, "
                "done INTEGER NOT NULL DEFAULT 0)"
            )
            count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            if count == 0:
                conn.executemany(
                    "INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS
                )
    finally:
        conn.close()


init_db()


@app.get("/", summary="API info", description="Describes this API and its endpoints.")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", description="Confirms the server is alive.")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List tasks", description="Returns every task in the database.")
def list_tasks():
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [Task(**dict(row)) for row in rows]


@app.get(
    "/tasks/{task_id}",
    summary="Get one task",
    description="Returns a single task by id, or 404 if it doesn't exist.",
)
def get_task(task_id: int):
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    if row is None:
        return JSONResponse(
            status_code=404, content={"error": f"Task {task_id} not found"}
        )
    return Task(**dict(row))


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a new task from a title. Returns 400 if title is missing or empty.",
)
def create_task(body: TaskCreate):
    if not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})
    with closing(get_db()) as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", (body.title, 0)
        )
        conn.commit()
    return Task(id=cursor.lastrowid, title=body.title, done=False)


@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description="Replaces a task's title and/or done state. 404 if unknown id, 400 if the body is empty or invalid.",
)
def update_task(task_id: int, body: TaskUpdate):
    if body.title is None and body.done is None:
        return JSONResponse(
            status_code=400, content={"error": "title or done is required"}
        )
    if body.title is not None and not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title cannot be empty"})
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404, content={"error": f"Task {task_id} not found"}
            )
        task = Task(**dict(row))
        if body.title is not None:
            task.title = body.title
        if body.done is not None:
            task.done = body.done
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (task.title, int(task.done), task.id),
        )
        conn.commit()
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Removes a task. Returns 204 with no body, or 404 if unknown id.",
)
def delete_task(task_id: int):
    with closing(get_db()) as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    if cursor.rowcount == 0:
        return JSONResponse(
            status_code=404, content={"error": f"Task {task_id} not found"}
        )
    return None
