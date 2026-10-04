# Task API

A small to-do list CRUD API built with FastAPI. Tasks are stored in a Postgres database using Docker container, and they survive server restarts.

## The one-command run
```powershell
Copy-Item .env.example .env then docker compose up
```

## Endpoints

| Method | Path          | Description                        | Success | Errors                                  |
|--------|---------------|------------------------------------|---------|-----------------------------------------|
| GET    | `/`           | API info                           | 200     | —                                       |
| GET    | `/health`     | Health check                       | 200     | —                                       |
| GET    | `/tasks`      | List all tasks                     | 200     | —                                       |
| GET    | `/tasks/{id}` | Get one task                       | 200     | 404 unknown id                          |
| POST   | `/tasks`      | Create a task (`{"title": "..."}`) | 201     | 400 missing/empty title                 |
| PUT    | `/tasks/{id}` | Update a task's title and/or done  | 200     | 404 unknown id, 400 empty body or title |
| DELETE | `/tasks/{id}` | Delete a task                      | 204     | 404 unknown id                          |

Values of the wrong type (e.g. `"done": "yes"`) are rejected by FastAPI with 422.


## Example request
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/tasks" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"title":"Do the dishes"}'
```

```
id title          done
-- -----          ----
4  Do the dishes  False
```

## .env variables
```
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=tasks
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/tasks
```


## Swagger UI

![Swagger UI showing all task endpoints](screenshots/07-swagger-endpoints.png)

## Docker run command

```powershell
 docker run --name taskdb -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=tasks -p 5432:5432 -v taskdata:/var/lib/postgresql/data -d postgres:17
 ```

 ## run this to reset database
 ```powershell
 docker compose down -v
 ```