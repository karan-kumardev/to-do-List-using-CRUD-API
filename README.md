# Task API — CRUD with FastAPI + Postgres (Dockerized)

A CRUD API for managing a to-do list, built with FastAPI as part of the FlyRank Internship (Backend Track). The storage layer has evolved across three assignments in this same repo:

1. **Week 2 (A1)** — in-memory list (gone on restart)
2. **Week 3 (A2)** — SQLite file (`tasks.db`), survives a restart
3. **Week 1 (A3, this version)** — PostgreSQL running in Docker, with the whole stack (app + database) started by a single `docker compose up`

The API's endpoints and response shapes have stayed identical through all three — only the storage engine underneath changed each time.

## What this is

A REST API supporting Create, Read, Update, and Delete on a list of tasks, persisted in a containerized PostgreSQL database. The app itself also runs in a container, and Docker Compose starts both together.

## Why Postgres + Docker

SQLite (A2) was a single file — simple, but not how real production backends usually store data. Postgres is a proper database *server*, the same kind of engine used by large-scale backends (including FlyRank's own stack). Running it in Docker means no manual Postgres install, no version conflicts, and the exact same setup on any machine — "works on my machine" stops being a meaningful excuse. A named Docker volume keeps the data safe even if the containers are torn down and rebuilt.

## How to run it

1. Clone this repo and move into the project folder:
   ```
   git clone <your-repo-url>
   cd todo-api
   ```
2. Copy the example environment file:
   ```
   cp .env.example .env
   ```
   (`.env` is git-ignored; `.env.example` shows which variables are needed. For local dev the default values work as-is.)
3. Start the whole stack — app and database together:
   ```
   docker compose up
   ```
4. Visit `http://127.0.0.1:8000` to confirm it's running, or `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

On first run, Docker builds the app image, pulls the official `postgres:16` image, and the app automatically creates the `tasks` table and seeds 3 example tasks (only if the table is empty). Data persists in a named volume (`taskdata`) — running `docker compose down` then `docker compose up` again does not lose your data.

### Environment variables

| Variable | Example | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgres://postgres:dev@db:5432/tasks` | Connection string the app uses to reach Postgres. Inside Compose, the host is `db` (the service name), not `localhost`. |

## Endpoints

| Method | Path            | Description                        | Success | Error(s)         |
|--------|-----------------|-------------------------------------|---------|-------------------|
| GET    | `/`             | API info                            | 200     | —                 |
| GET    | `/tasks`        | List all tasks                      | 200     | —                 |
| GET    | `/tasks/{id}`   | Get a single task by id             | 200     | 404 if not found  |
| POST   | `/tasks`        | Create a new task (`{"title": ...}`, `done` optional, defaults to false) | 201 | 400 if title empty |
| PUT    | `/tasks/{id}`   | Update a task's title and done status | 200   | 400 empty / 404 not found |
| DELETE | `/tasks/{id}`   | Delete a task                       | 204     | 404 if not found  |

All CRUD operations use parameterized SQL queries (`%s` placeholders via `psycopg`) — no user input is ever inserted directly into a query string.

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

With the stack running, open a `psql` prompt inside the database container:
```
docker exec -it todo-api-db-1 psql -U postgres -d tasks
```

```
[ INSERT SCREENSHOT HERE — psql \dt and a SELECT * FROM tasks; showing your data ]
```

## Persistence, proven

Created a task via POST, then ran `docker compose down` (removing both containers) followed by `docker compose up` again. `GET /tasks` still showed the created task afterward — confirming the named volume (`taskdata`) kept the data safe across a full stack teardown and rebuild, not just an app restart.

## Notes

- Data lives in Postgres, inside a named Docker volume (`taskdata`) — it survives `docker compose down`/`up`, but would be lost if the volume itself were deleted (`docker compose down -v`).
- Task IDs are assigned automatically by the database (`SERIAL PRIMARY KEY`), never supplied by the client.
- The 3 seed tasks are inserted only on the very first run (when the table is empty) — restarting does not duplicate them.
- `.env` is git-ignored; only `.env.example` (with placeholder-safe values) is committed. No credentials are hardcoded anywhere in the source.
- Inside the Compose network, the app reaches Postgres via the service name `db`, not `localhost` — this is different from running the app locally against a manually-started container (Stage 0–3), where `localhost` was used.