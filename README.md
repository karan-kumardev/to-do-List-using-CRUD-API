# Task API — CRUD with FastAPI + Postgres + Supabase Auth (Dockerized)

A CRUD API for managing a to-do list, built with FastAPI as part of the FlyRank Internship (Backend Track). The storage layer and feature set have evolved across four assignments in this same repo:

1. **Week 2 (A1)** — in-memory list (gone on restart)
2. **Week 3 (A2)** — SQLite file (`tasks.db`), survives a restart
3. **Week 1 (A3)** — PostgreSQL running in Docker, with the whole stack (app + database) started by a single `docker compose up`
4. **Week 2 (A4, this version)** — Supabase Auth added: sign up, log in, log out, JWT verification, and protected routes — the API is no longer wide open to anyone who knows the URL

The task CRUD endpoints and response shapes have stayed identical through all four stages — only the storage engine (A1→A3) and now the security layer (A4) have changed.

## What this is

A REST API supporting Create, Read, Update, and Delete on a list of tasks, persisted in a containerized PostgreSQL database — now sitting behind a real authentication layer. Accounts, password hashing, and JWT signing are handled entirely by **Supabase Auth** (an external Identity Provider); this app never stores a password or writes any cryptography itself. It only ever sends credentials to Supabase and verifies the tokens Supabase hands back.

## Why Postgres + Docker

SQLite (A2) was a single file — simple, but not how real production backends usually store data. Postgres is a proper database *server*, the same kind of engine used by large-scale backends (including FlyRank's own stack). Running it in Docker means no manual Postgres install, no version conflicts, and the exact same setup on any machine — "works on my machine" stops being a meaningful excuse. A named Docker volume keeps the data safe even if the containers are torn down and rebuilt.

## Why Supabase Auth

Rolling your own password hashing and token signing is a well-known way to introduce serious security bugs. Supabase acts as a trusted Identity Provider: it stores accounts, hashes passwords, and issues signed JSON Web Tokens (JWTs). This app's job is just the part that matters for a backend developer — receiving a token on each request, asking Supabase whether it's genuine, and opening (or refusing) the door accordingly.

**The trust triangle:**

| Step | Who does it | What happens |
|---|---|---|
| 1. Sign up / Log in | Client → Supabase | Client sends email + password to Supabase |
| 2. The token | Supabase → Client | Supabase verifies credentials, returns a JWT |
| 3. The request | Client → this API | Client calls a protected route with the JWT in an `Authorization` header |
| 4. Verification | This API → Supabase | The API asks Supabase "is this token real?" — opens the door if yes |

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
   Then fill in your own Supabase Project URL and publishable key (see below). `.env` is git-ignored; `.env.example` shows which variables are needed.
3. Start the whole stack — app and database together:
   ```
   docker compose up --build
   ```
4. Visit `http://127.0.0.1:8000` to confirm it's running, or `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

On first run, Docker builds the app image, pulls the official `postgres:16` image, and the app automatically creates the `tasks` table and seeds 3 example tasks (only if the table is empty). Data persists in a named volume (`taskdata`) — running `docker compose down` then `docker compose up` again does not lose your data.

### Environment variables

| Variable | Example | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgres://postgres:dev@db:5432/tasks` | Connection string the app uses to reach Postgres. Inside Compose, the host is `db` (the service name), not `localhost`. |
| `SUPABASE_URL` | `https://xxxxxxxxxxxx.supabase.co` | Your Supabase project's base URL. |
| `SUPABASE_KEY` | `sb_publishable_...` | Supabase's publishable (anon) key — safe to use client-side. Never use the `service_role`/secret key here. |
| `PORT` | `8000` | Port the app listens on. |

## Endpoints

### Auth (Supabase-backed)

| Method | Path | Description | Auth required | Success | Error(s) |
|---|---|---|---|---|---|
| POST | `/auth/signup` | Create a new account via Supabase | No | 201 | 400 missing fields |
| POST | `/auth/login` | Log in, returns an access token + refresh token | No | 200 | 400 missing fields, 401 invalid credentials |
| POST | `/auth/logout` | End the current session | Yes | 204 | 401 missing/invalid token |

### Public & protected

| Method | Path | Description | Auth required | Success | Error(s) |
|---|---|---|---|---|---|
| GET | `/public/info` | Open, unauthenticated info endpoint | No | 200 | — |
| GET | `/protected/profile` | Returns the logged-in user's own profile | Yes | 200 | 401 missing/invalid/expired token |
| GET | `/protected/dashboard` | Second example protected route, reusing the same guard | Yes | 200 | 401 missing/invalid/expired token |

### Tasks (CRUD, unchanged since A3)

| Method | Path | Description | Success | Error(s) |
|---|---|---|---|---|
| GET | `/` | API info | 200 | — |
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{id}` | Get a single task by id | 200 | 404 if not found |
| POST | `/tasks` | Create a new task (`{"title": ...}`, `done` optional, defaults to false) | 201 | 400 if title empty |
| PUT | `/tasks/{id}` | Update a task's title and done status | 200 | 400 empty / 404 not found |
| DELETE | `/tasks/{id}` | Delete a task | 204 | 404 if not found |

All CRUD operations use parameterized SQL queries (`%s` placeholders via `psycopg`) — no user input is ever inserted directly into a query string.

## How auth is enforced

Protected routes (`/protected/profile`, `/protected/dashboard`, `/auth/logout`) all share a single reusable dependency (`verify_token`), built with FastAPI's `HTTPBearer` security scheme:

1. The client sends `Authorization: Bearer <token>` on the request.
2. The dependency extracts the token and calls `supabase.auth.get_user(token)` — a real network call to Supabase, not a local check.
3. If the token is missing, malformed, tampered with, or expired, the request is rejected with `401` before the route body ever runs.
4. If valid, the route receives the verified user and executes normally.

Adding a new protected route is just a matter of declaring `Depends(verify_token)` on it — no auth logic is duplicated per route.

## Example requests

**Sign up:**
```
curl -i -X POST http://127.0.0.1:8000/auth/signup -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

**Log in:**
```
curl -i -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

**Call a protected route:**
```
curl -i http://127.0.0.1:8000/protected/profile -H "Authorization: Bearer <your_access_token>"
```

**Create a task (unchanged from A3):**
```
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

See `screenshots/swagger-tasks-endpoints.png` for the full task endpoints list, and `screenshots/curl-get-tasks.png` for a live `GET /tasks` call and response.

## Swagger UI

All auth and task endpoints were tested via the interactive `/docs` page. Auth and protected routes show a lock icon; clicking **Authorize** and pasting a valid access token applies it automatically to every subsequent "Try it out" call.

![Swagger — auth routes with Authorize button](./screenshots/swagger-auth-routes.png)
![Swagger — protected routes showing lock icons](./screenshots/swagger-protected-locks.png)
![Swagger — Authorize modal, token accepted](./screenshots/swagger-authorize-modal.png)
![Swagger — /protected/profile returning 200 with real user data](./screenshots/swagger-protected-profile-200.png)

## Exploring the database directly

Task data was inspected directly using **DB Browser for SQLite**, browsing the `tasks` table and running SQL updates against it.

![DB Browser — tasks table contents](./screenshots/db-browser-tasks.png)
![DB Browser — running an UPDATE query](./screenshots/db-browser-update-query.png)

Note: user accounts are **not** in this database — Supabase manages its own separate `auth.users` table on its side. This project's Postgres database only ever holds task data.

## Persistence, proven

Created a task via POST, then ran `docker compose down` (removing both containers) followed by `docker compose up` again. `GET /tasks` still showed the created task afterward — confirming the named volume (`taskdata`) kept the data safe across a full stack teardown and rebuild, not just an app restart.

## Notes

- Data lives in Postgres, inside a named Docker volume (`taskdata`) — it survives `docker compose down`/`up`, but would be lost if the volume itself were deleted (`docker compose down -v`).
- Task IDs are assigned automatically by the database (`SERIAL PRIMARY KEY`), never supplied by the client.
- The 3 seed tasks are inserted only on the very first run (when the table is empty) — restarting does not duplicate them.
- `.env` is git-ignored; only `.env.example` (with placeholder-safe values) is committed. No credentials — database or Supabase — are hardcoded anywhere in the source.
- Inside the Compose network, the app reaches Postgres via the service name `db`, not `localhost` — this is different from running the app locally against a manually-started container, where `localhost` was used.
- No password is ever stored or hashed by this app — Supabase owns that entirely. No cryptography is written here.
- The Supabase publishable (anon) key is safe to expose; the `service_role`/secret key is never used in this project and must never be committed.