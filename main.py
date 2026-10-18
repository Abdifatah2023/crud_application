from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


import repository
from auth import Unauthorized, get_bearer_token, get_current_user


app = FastAPI(
    title="Task API",
    description="A small to-do list API. Tasks live in Postgres; user accounts and JWTs are managed by Supabase Auth.",
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

class UserSignup(BaseModel):
    email: str = ""
    password: str = ""

repository.init_db()


@app.exception_handler(Unauthorized)
def unauthorized_handler(request: Request, exc: Unauthorized):
    return JSONResponse(status_code=401, content={"error": exc.message})


@app.get("/", summary="API info", description="Describes this API and its endpoints.")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/auth/signup", "/auth/login", "/auth/logout", "/public/info", "/protected/profile", "/protected/dashboard"],
    }


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


@app.post(
    "/auth/signup",
    status_code=201,
    summary="Sign up a new user",
    description="Creates a new user account. Returns 400 if the email or password is missing.",
)
def user_signup(body: UserSignup):
    return repository.create_user(body.email, body.password)

@app.post(
    "/auth/login",
    status_code=200,
    summary="Log in a user",
    description="Logs in a user and returns an access token. Returns 400 if the email or password is missing.",
)
def user_login(body: UserSignup):
    return repository.login_user(body.email, body.password)

@app.get(
    "/public/info",
    status_code=200,
    summary="Public info",
    description="Returns public information about the API.",
)
def public_info():
    return JSONResponse(status_code=200, content={"message": "Welcome stranger! This info is public."})

@app.get(
    "/protected/profile",
    summary="Protected profile",
    description="Requires 'Authorization: Bearer <token>'. Verifies the token with Supabase and returns the user's id, "
    "email and account-created date. Returns 401 if the token is missing, malformed, invalid or expired.",
)
def protected_profile(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@app.get(
    "/protected/dashboard",
    summary="Protected dashboard",
    description="Requires 'Authorization: Bearer <token>'. Greets the logged-in user. "
    "Returns 401 if the token is missing, malformed, invalid or expired.",
)
def protected_dashboard(user=Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {user.email}!"}


@app.post(
    "/auth/logout",
    status_code=204,
    dependencies=[Depends(get_current_user)],
    summary="Log out",
    description="Requires 'Authorization: Bearer <token>'. Ends the user's Supabase session and returns 204 "
    "with no body. Returns 401 if the token is missing, malformed, invalid or expired.",
)
def user_logout(token: str = Depends(get_bearer_token)):
    error = repository.logout_user(token)
    if error is not None:
        return error
    return Response(status_code=204)
