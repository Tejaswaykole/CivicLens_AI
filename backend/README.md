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
| `API_HOST` | Listen address. It must match Uvicorn's `--host`. Loopback names (`127.0.0.1`, `localhost`, `::1`, and the rest of `127.0.0.0/8`) match each other. |
| `JWT_SECRET` | HS256 signing secret. At least 32 characters and 8 distinct characters. Do not use the example placeholder. |
| `JWT_ALGORITHM` | Must be `HS256`. |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime. Allowed range is 5 to 1440. Default is 30. |
| `ENABLE_API_DOCS` | Production hides the docs unless this is `true`. |
| `AUTH_LOGIN_RATE_LIMIT` | Limit for `POST /auth/login`. Default `10/minute`. |
| `AUTH_REGISTER_RATE_LIMIT` | Limit for `POST /auth/register`. Default `5/minute`. |
| `EMAIL_VERIFICATION_DEBUG` | Development and test only. Returns the verification token in the register response. |
| `EMAIL_VERIFICATION_TTL_HOURS` | Verification token lifetime, from 1 to 72 hours. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM` | Reserved placeholders. Email is not sent. |
| `SEED_DEV_PASSWORD` | Optional local password for the fictional seed accounts. Only a hash is stored. |

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

`alembic downgrade base` drops the schema. Do not run it against a database you need to keep. Revision `20261020_0002` adds account audit labels. Its own downgrade is a no-op because PostgreSQL cannot remove one enum label safely. Revision `20261020_0003` adds email verification columns and marks existing accounts verified. This project does not drop or reset a database automatically.

## Optional development seed

Seeding does not run on startup. It creates four fictional departments aligned with the frontend codes (`PWD`, `DJB`, `MCD`, `BSES`) and four `example.com` development users. It does not create complaints, predictions, or metrics. If `SEED_DEV_PASSWORD` is set, the command stores an Argon2id hash and does not print the password. If it is unset, those accounts stay unable to log in.

```powershell
python -m app.seed
```

Running it again updates those same rows instead of duplicating them. It exits immediately when `APP_ENV=production`.

## Run the API locally

Bind to loopback. `--host` must match `API_HOST`:

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

## Authentication

Passwords are hashed with Argon2id and are never returned. Access tokens are HS256 JWTs signed with `JWT_SECRET`. The token carries the user id, issue time, and expiry. The role is loaded from the database on each request, so a role change or deactivation applies immediately.

Generate a signing secret locally. The application does not create one for you:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put that value in `JWT_SECRET`. Local development can omit it when both `API_HOST` and Uvicorn's `--host` are loopback and `APP_ENV` is not `production`. Login then returns HTTP 503 until a secret is set. `APP_ENV=production`, or a bind address outside loopback, refuses to start when the secret is missing, short, a placeholder, or made of fewer than 8 distinct characters.

`API_HOST` and `--host` are checked together. Loopback names agree with each other. This fails during startup and does not serve the API:

```powershell
# API_HOST=127.0.0.1 in .env, while the process listens on every interface
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run local work on loopback. The `--host` value below matches the default `API_HOST`:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

With `--reload` or more than one worker, Uvicorn opens the socket before the app process starts. If the bind address is rejected, that process exits before it accepts requests. Stop the reloader as well so the port is not left open.

Public routes:

- `GET /api/v1/health`
- `POST /api/v1/auth/register` creates an unverified citizen. A `role` field is rejected.
- `POST /api/v1/auth/login` accepts email and password.
- `POST /api/v1/auth/verify-email` accepts a verification token.

Every other route requires `Authorization: Bearer <access_token>`.

| Role | What the server allows |
| --- | --- |
| Citizen | Read only their own complaints. Submit a complaint only after email verification. Read their own notifications and unread role notices addressed to citizens. Read departments. Cannot change status, assign, review, list users, or read the audit log. |
| Department officer | Complaints already assigned to their department. Field status updates (`assigned`, `in_progress`, `resolved`) and reassignment only inside that department. Staff profiles in that department. Their own notifications. |
| Grievance officer | All complaints. Triage statuses (`in_review`, `triaged`, `rejected`), assignment to an active department, and human review. Staff profiles, not citizen profiles. |
| System administrator | Any workflow-legal status change, all complaints, staff creation and account updates, and the audit log. An administrator cannot change their own role or deactivate their own account. |

`actor_user_id` and `reviewer_user_id` must match the token when they are sent. `actor_verified` is true when the stored actor is a user id. `GET /health` still reports `authenticated: false` because that request does not identify a person.

Expected auth errors:

| HTTP | `code` | When |
| --- | --- | --- |
| 401 | `not_authenticated` | No bearer token |
| 401 | `invalid_token` | Bad, expired, or unknown-user token |
| 401 | `invalid_credentials` | Login failed. The message does not say which part failed. |
| 401 | `inactive_account` | A valid token belongs to a deactivated user |
| 403 | `forbidden` | The caller can see the resource but cannot perform the action |
| 403 | `email_unverified` | A citizen must verify an email before submitting a complaint |
| 404 | `not_found` | The row is missing, or the caller is not allowed to see it |
| 409 | `duplicate_email` | Registration or staff creation reused an email |
| 429 | `rate_limited` | Login or registration exceeded the in-process limit |
| 503 | `auth_not_configured` | `JWT_SECRET` is missing or not strong enough |

Login and registration limits default to 10 and 5 requests per minute for each client address. The counters are stored in process memory with the `limits` library, so they reset on restart and are not shared by multiple workers. A failed login still uses the same generic message. The limiter does not record the password or the token. This is not sufficient for a multi-host deployment.

Public registration stores only a SHA-256 hash of a verification token and an expiry. The raw token is not logged. With `EMAIL_VERIFICATION_DEBUG=true` in development or test, the register response includes `dev_verification_token` so you can call `POST /auth/verify-email`. Production refuses that flag. `SMTP_*` and `EMAIL_FROM` are placeholders only: this build does not send email, so a production registration cannot be verified until a mail provider is added. Existing accounts are marked verified by migration `20261020_0003`. An unverified citizen can log in and cannot submit a complaint.

`APP_ENV=production` serves neither `/docs`, `/redoc`, nor `/openapi.json` unless `ENABLE_API_DOCS=true`. Do not deploy this API on a public network until the signing secret and database URL come from a secret store.

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
