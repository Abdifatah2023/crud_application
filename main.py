from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    done: bool


tasks = [
    Task(id=1, title="Buy milk", done=False),
    Task(id=2, title="Walk the dog", done=False),
    Task(id=3, title="Read a book", done=True),
]


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    return JSONResponse(
        status_code=404, content={"error": f"Task {task_id} not found"}
    )
