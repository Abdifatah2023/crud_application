# Task API

A small to-do list CRUD API built with FastAPI. Data is stored in memory — it resets whenever the server restarts (there's no database yet).

## Install & run

```
python -m venv .venv
.venv\Scripts\activate
pip install fastapi "uvicorn[standard]"
uvicorn main:app --port 8000
```

The API is now running at `http://localhost:8000`. Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

## Endpoints

| Method | Path           | Description                          | Success | Errors           |
|--------|----------------|--------------------------------------|---------|-------------------|
| GET    | `/`            | API info                             | 200     | —                 |
| GET    | `/health`      | Health check                         | 200     | —                 |
| GET    | `/tasks`       | List all tasks                       | 200     | —                 |
| GET    | `/tasks/{id}`  | Get one task                         | 200     | 404 unknown id    |
| POST   | `/tasks`       | Create a task (`{"title": "..."}`)   | 201     | 400 missing/empty title |
| PUT    | `/tasks/{id}`  | Update a task's title and/or done    | 200     | 404 unknown id, 400 empty/invalid body |
| DELETE | `/tasks/{id}`  | Delete a task                        | 204     | 404 unknown id    |

## Example request

```
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
date: Fri, 11 Sep 2026 04:35:17 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Exploring the database

I opened `tasks.db` in DB Browser for SQLite and ran SQL by hand while the API was running.

```sql
DELETE FROM tasks WHERE done=1;
```

After marking every task done with `UPDATE tasks SET done=1;`, this query deleted all 3 rows ("3 rows affected"), and `GET /tasks` immediately returned `[]` with no server restart, because the API and DB Browser read the same file.

![DB Browser running the DELETE query next to GET /tasks returning an empty list](screenshots/06-delete-done.png)

## Swagger UI

![Swagger UI showing all task endpoints](docs/swagger-screenshot.png)
