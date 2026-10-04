from contextlib import closing
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import repository


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


repository.init_db()

@app.get("/", summary="API info", description="Describes this API and its endpoints.")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", description="Confirms the server is alive.")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List tasks", description="Returns every task in the database.")
def list_tasks():
    return repository.list_tasks()


@app.get(
    "/tasks/{task_id}",
    summary="Get one task",
    description="Returns a single task by id, or 404 if it doesn't exist.",
)
def get_task(task_id: int):
    return repository.get_task(task_id)


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a task",
    description="Creates a new task from a title. Returns 400 if title is missing or empty.",
)
def create_task(body: TaskCreate):
    return repository.create_task(body.title)


@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description="Replaces a task's title and/or done state. 404 if unknown id, 400 if the body is empty or invalid.",
)
def update_task(task_id: int, body: TaskUpdate):
    return repository.update_task(task_id, body.title, body.done)


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Removes a task. Returns 204 with no body, or 404 if unknown id.",
)
def delete_task(task_id: int):
    return repository.delete_task(task_id)
