import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    description="A small in-memory to-do list API (no database yet — data resets on restart).",
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


tasks = [
    Task(id=1, title="Buy milk", done=False),
    Task(id=2, title="Walk the dog", done=False),
    Task(id=3, title="Read a book", done=True),
]


@app.get("/", summary="API info", description="Describes this API and its endpoints.")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", description="Confirms the server is alive.")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List tasks", description="Returns every task in memory.")
def list_tasks():
    return tasks


@app.get(
    "/tasks/{task_id}",
    summary="Get one task",
    description="Returns a single task by id, or 404 if it doesn't exist.",
)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    return JSONResponse(
        status_code=404, content={"error": f"Task {task_id} not found"}
    )


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a new task from a title. Returns 400 if title is missing or empty.",
)
def create_task(body: TaskCreate):
    if not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})
    next_id = max((task.id for task in tasks), default=0) + 1
    task = Task(id=next_id, title=body.title, done=False)
    tasks.append(task)
    return task


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
    for task in tasks:
        if task.id == task_id:
            if body.title is not None:
                task.title = body.title
            if body.done is not None:
                task.done = body.done
            return task
    return JSONResponse(
        status_code=404, content={"error": f"Task {task_id} not found"}
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Removes a task. Returns 204 with no body, or 404 if unknown id.",
)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return None
    return JSONResponse(
        status_code=404, content={"error": f"Task {task_id} not found"}
    )
