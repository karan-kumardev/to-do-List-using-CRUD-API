# Task API — CRUD with FastAPI

A small in-memory CRUD API for managing a to-do list, built with FastAPI as part of the FlyRank Internship (Backend Track, Week 2, Assignment A1).

## What this is

A REST API that supports Create, Read, Update, and Delete operations on a list of tasks. Data lives in memory only — restarting the server resets it to the 3 seed tasks (no database yet, that's next week).

## How to run it

1. Clone this repo and move into the project folder:
   ```
   git clone <your-repo-url>
   cd todo-api
   ```
2. Install dependencies:
   ```
   pip install fastapi uvicorn
   ```
3. Start the server:
   ```
   uvicorn main:app --reload
   ```
4. Visit `http://127.0.0.1:8000` to confirm it's running, or `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Endpoints

| Method | Path            | Description                        | Success | Error(s)         |
|--------|-----------------|-------------------------------------|---------|-------------------|
| GET    | `/`             | API info                            | 200     | —                 |
| GET    | `/tasks`        | List all tasks                      | 200     | —                 |
| GET    | `/tasks/{id}`   | Get a single task by id             | 200     | 404 if not found  |
| POST   | `/tasks`        | Create a new task (`{"title": ...}`)| 201     | 400 if title empty|
| PUT    | `/tasks/{id}`   | Update a task's title               | 200     | 400 empty / 404 not found |
| DELETE | `/tasks/{id}`   | Delete a task                       | 204     | 404 if not found  |

## Example request

```
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

```
[ PASTE YOUR ACTUAL curl -i OUTPUT HERE — full response including status line and JSON body ]
```

## Swagger UI

The full CRUD cycle (create, list, update, delete) was tested via the interactive `/docs` page.

```
[ INSERT YOUR SWAGGER UI SCREENSHOT HERE — showing endpoints list and a successful "Try it out" call ]
```

## Notes

- No database — all data is in-memory and resets on server restart.
- Task IDs are assigned automatically by the server, never supplied by the client.
