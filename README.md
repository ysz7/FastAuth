# FastAuth

![Tests](https://github.com/ysz7/FastAuth/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

Production-ready authentication service built with FastAPI. Supports JWT access/refresh tokens, rate limiting, structured logging, and is fully containerised.

---

## Features

- JWT authentication with access & refresh tokens
- Secure password hashing via bcrypt
- Token revocation on logout (Redis blacklist)
- Rate limiting per endpoint (slowapi)
- Structured JSON logging
- Database migrations with Alembic
- Full test suite (pytest-asyncio, SQLite in-memory, fakeredis)
- CI via GitHub Actions

---

## Stack

| Layer       | Technology              |
|-------------|-------------------------|
| API         | FastAPI + Uvicorn       |
| Database    | PostgreSQL + SQLAlchemy |
| Cache       | Redis                   |
| Auth        | JWT (python-jose)       |
| Migrations  | Alembic                 |
| Tests       | pytest + pytest-asyncio |

---

## Quick Start (Docker)

```bash
git clone https://github.com/ysz7/FastAuth.git
cd FastAuth
cp .env.example .env
docker compose up --build
```

API available at `http://localhost:8000`.  
Swagger UI — `http://localhost:8000/docs`.

---

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # set DATABASE_URL and REDIS_URL

alembic upgrade head
uvicorn app.main:app --reload
```

---

## API Endpoints

| Method | Endpoint                 | Description               | Auth |
|--------|--------------------------|---------------------------|------|
| POST   | `/auth/register`         | Register a new user       | —    |
| POST   | `/auth/login`            | Login, receive tokens     | —    |
| POST   | `/auth/refresh`          | Refresh access token      | —    |
| POST   | `/auth/logout`           | Revoke refresh token      | ✓    |
| GET    | `/auth/me`               | Get current user info     | ✓    |
| POST   | `/auth/change-password`  | Change password           | ✓    |

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use SQLite in-memory and fakeredis — no external services required.

---

## Environment Variables

| Variable                      | Default    | Description                   |
|-------------------------------|------------|-------------------------------|
| `DATABASE_URL`                | —          | PostgreSQL connection string  |
| `REDIS_URL`                   | —          | Redis connection string       |
| `SECRET_KEY`                  | `changeme` | JWT signing key               |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`       | Access token TTL (minutes)    |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`        | Refresh token TTL (days)      |

---

## License

MIT
