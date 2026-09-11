from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


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


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    if not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})
    next_id = max((task.id for task in tasks), default=0) + 1
    task = Task(id=next_id, title=body.title, done=False)
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}")
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


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return None
    return JSONResponse(
        status_code=404, content={"error": f"Task {task_id} not found"}
    )
