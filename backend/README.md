# CivicLens AI backend

Phase 3 foundation for the CivicLens grievance API: FastAPI, PostgreSQL, SQLAlchemy 2.0, and Alembic.

This service is **not authenticated**. Do not expose it on a public network. Login and authorization belong to a later phase. The API does not run a machine-learning model and does not invent priorities, confidence scores, or explanations.

The React frontend on `main` is unchanged. It still uses mock data.

## Python version

Use Python 3.11. The dependency set is also expected to work on newer 3.11-compatible releases, and development was checked with the Python 3.11 interpreter.

## Virtual environment

From the `backend` directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Environment variables

Copy the example file and replace the placeholders. Do not commit `.env`.

```powershell
Copy-Item .env.example .env
```

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | `development`, `test`, or `production`. The seed command refuses `production`. |
| `APP_NAME` | API title. |
| `DATABASE_URL` | PostgreSQL URL. `postgresql://` and `postgres://` are normalized to `postgresql+psycopg://`. |
| `CORS_ORIGINS` | Comma-separated browser origins. The default is the Vite dev server. |
| `CORS_ALLOW_CREDENTIALS` | Keep `false` in this phase. A wildcard origin combined with credentials is rejected. |
| `SEED_LABEL` | Optional label for operators. It is not a password. |

There is no hosted database in this repository. Create a local database, or supply your own PostgreSQL URL (including a Supabase Postgres URL). Hosted Postgres usually needs `sslmode=require` in the URL. Do not disable TLS verification.

Example, with placeholders:

```text
postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/civiclens
```

PostgreSQL 13 or newer is required because primary keys use `gen_random_uuid()`.

SQLite is rejected. PostgreSQL-specific constraints and indexes are part of the schema.

## Database setup

Create an empty database with your own PostgreSQL tools, then apply migrations. Example for a local superuser:

```sql
CREATE DATABASE civiclens;
```

For tests, use a **different** database whose name contains `_test`:

```sql
CREATE DATABASE civiclens_test;
```

## Alembic

Run these commands from the `backend` directory so `DATABASE_URL` is loaded from `.env` or the shell. Alembic does not store a real password in `alembic.ini`.

Check the current revision:

```powershell
alembic current
```

Show migration history:

```powershell
alembic history
```

Apply migrations:

```powershell
alembic upgrade head
```

Generate a later migration after changing the models:

```powershell
alembic revision --autogenerate -m "describe the change"
```

Inspect status before and after applying:

```powershell
alembic current
alembic heads
```

`alembic downgrade` drops the Phase 3 schema. Do not run it against a database you need to keep. This project does not drop or reset a database automatically.

## Optional development seed

Seeding does not run on startup. It creates four fictional departments aligned with the frontend codes (`PWD`, `DJB`, `MCD`, `BSES`) and four `example.com` development users. It does not create complaints, predictions, metrics, or password hashes.

```powershell
python -m app.seed
```

Running it again updates those same rows instead of duplicating them. It exits immediately when `APP_ENV=production`.

## Run the API locally

Bind to localhost only:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Interactive docs: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- Health: `http://127.0.0.1:8000/api/v1/health`

Health returns `database: ok` only after `SELECT 1` succeeds. If `DATABASE_URL` is missing, the response is HTTP 503 with `database: not_configured`. A connection failure is `database: unavailable`. The process does not claim the database is healthy without that check.

## Tests

Unit tests do not need PostgreSQL:

```powershell
pytest
```

PostgreSQL tests run only when `TEST_DATABASE_URL` points at a PostgreSQL database whose name contains `_test`. They apply `alembic upgrade head` and roll back each test's data. They do not downgrade or delete an existing database.

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/civiclens_test"
pytest
```

If that variable is unset, the PostgreSQL tests are skipped and the skip message says so.

Lint:

```powershell
ruff check app tests alembic
```

## Authentication limitations

Every endpoint under `/api/v1` is unprotected:

- `GET /health`
- `GET /users` and `GET /users/{user_id}`
- `GET /departments` and `GET /departments/{department_id}`
- `GET` and `POST /complaints`, and `PATCH /complaints/{complaint_id}/status`
- `POST /complaints/{complaint_id}/assignments`
- `POST /complaints/{complaint_id}/reviews`
- `GET /audit-logs`
- `GET /notifications` and `PATCH /notifications/{notification_id}/read`

A user id in a request body is stored as a reference after checking that the row exists. It is not a login, a JWT, or proof of identity. `actor_verified` is always `false`. The frontend development role switcher is not an authorization mechanism. Password hashes, when a later phase stores them, are never included in responses. Do not deploy this API publicly.

## Machine-learning limitations

There is no inference endpoint. Creating a complaint does not write a prediction, confidence score, or explanation. The `model_predictions` table is reserved for a future model that actually produces those values. Human reviews keep a machine suggestion only when a stored prediction exists. A priority sent by the client is labeled `client_supplied` and is not presented as model output.

## Common database connection problems

- `DATABASE_URL` is missing: copy `.env.example` to `.env` and set a real URL.
- PostgreSQL is not running, or the host and port are wrong: the health check reports `unavailable`.
- The database named in the URL has not been created: create it before `alembic upgrade`.
- The password or user is wrong: the driver error stays in the server log. The API response does not include the URL or the password.
- A hosted database rejects non-TLS connections: add `sslmode=require`. Do not set `sslmode=disable` and do not turn off certificate verification.
- The URL uses `postgresql://` without a driver: the application rewrites it to `postgresql+psycopg://`. Installing this project pulls in Psycopg 3, not psycopg2.
- Alembic says the URL is not set: export `DATABASE_URL` or run it from `backend` with a `.env` file present.

## How the frontend connects later

Phase 7 is the integration phase. The frontend example env on `main` already has:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Keep the API on `http://127.0.0.1:8000` during local development and keep `CORS_ORIGINS` pointed at `http://localhost:5173`. The field mapping between the current TypeScript models and these responses is documented in `docs/frontend-api-contract.md`.

## Project layout

```text
backend/
  app/            FastAPI app, models, schemas, repositories, services
  alembic/        migration environment and versions
  tests/          unit tests and optional PostgreSQL tests
  docs/           frontend API contract
  requirements.txt
  .env.example
  alembic.ini
```
