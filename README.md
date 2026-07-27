# Task API — CRUD with FastAPI + SQLite

A CRUD API for managing a to-do list, built with FastAPI as part of the FlyRank Internship (Backend Track). Started as an in-memory API in Week 2 (Assignment A1); now backed by a real SQLite database (Week 3, Assignment A2) so data survives a server restart.

## What this is

A REST API that supports Create, Read, Update, and Delete operations on a list of tasks, persisted in a SQLite database (`tasks.db`). The API's endpoints and responses are unchanged from Week 2 — only the storage layer moved from an in-memory list to disk.

## Why SQLite

SQLite needs no separate server or install — the entire database is a single file (`tasks.db`), created automatically the first time the app runs. For a project this size, that meant zero setup friction while still getting real persistence: data now survives a restart, which an in-memory list never could.

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

On first run, `tasks.db` is created automatically with a `tasks` table, seeded with 3 example tasks. Restarting the server does not duplicate the seed data or reset your changes — everything is saved to disk.

## Endpoints

| Method | Path            | Description                        | Success | Error(s)         |
|--------|-----------------|-------------------------------------|---------|-------------------|
| GET    | `/`             | API info                            | 200     | —                 |
| GET    | `/tasks`        | List all tasks                      | 200     | —                 |
| GET    | `/tasks/{id}`   | Get a single task by id             | 200     | 404 if not found  |
| POST   | `/tasks`        | Create a new task (`{"title": ..., "done": ...}`)| 201 | 400 if title empty|
| PUT    | `/tasks/{id}`   | Update a task's title and done status | 200   | 400 empty / 404 not found |
| DELETE | `/tasks/{id}`   | Delete a task                       | 204     | 404 if not found  |

All CRUD operations use parameterized SQL queries (`?` placeholders) — no user input is ever inserted directly into a query string.

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

## Exploring the database directly

`tasks.db` can be opened in [DB Browser for SQLite](https://sqlitebrowser.org/) to inspect or edit data outside the API — both read and write the same file, so changes made in either place appear in the other with no restart needed.

```
[ INSERT DB BROWSER SCREENSHOT HERE — showing the tasks table and its rows ]
```

**Query run by hand in DB Browser:**
```sql
UPDATE tasks SET done = 1 WHERE id = 1;
```
**What it returned:** marked task 1 as complete directly in the database; confirmed via `GET /tasks/1` immediately afterward, which showed `"done": true` with no server restart — proving the API and DB Browser read the exact same file.

## Notes

- Data is stored in `tasks.db` (SQLite) and survives server restarts.
- Task IDs are assigned automatically by the database, never supplied by the client.
- The 3 seed tasks are inserted only on the very first run (when the table is empty) — restarting does not duplicate them.
