## Traffic Platform Full-Stack Solution

This repository delivers a production-oriented backend (FastAPI + PostgreSQL + Redis + Celery) and an Android client (Jetpack Compose + Hilt + Retrofit) for the Telegram-authenticated traffic sharing platform described in the specifications.

### Repository Layout

```
backend/            # FastAPI application, Alembic migrations, Celery tasks, tests
android/            # Android app (Kotlin, Compose, Hilt)
deployment/         # VPS deployment instructions
docker-compose.yml  # Local/production docker stack (backend + worker + db + redis)
```

### Backend Highlights

- Modular FastAPI app with layers for auth, dashboard, traffic sessions, pricing, balance, withdrawals, notifications, analytics, settings, support, and news
- Async SQLAlchemy models with Alembic migrations (`alembic/versions/0001_initial.py`)
- Redis-backed rate limiting and policy tracking for traffic sessions
- Celery workers for notifications, pricing updates, telemetry, and payout hooks (`app/tasks/*`)
- Configuration via `.env` (`backend/.env.example`)
- Test harness using pytest + httpx (`backend/tests/test_health.py`)

#### Local Backend Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .[test]
cp .env.example .env  # adjust values
alembic upgrade head
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

### Android Client Highlights

- Jetpack Compose UI with themed navigation and bottom bar
- Hilt dependency injection, Retrofit + Kotlin Serialization networking
- Feature screens for login, dashboard, traffic control, balance, analytics, news/promo, settings, and support
- BASE_URL configured via BuildConfig (`app/build.gradle.kts`)

#### Android Build

```bash
cd android
./gradlew assembleDebug
```

Install debug build on emulator/device. Debug build uses `http://10.0.2.2:8000`; release points to `https://113.30.191.89`.

### Docker Compose Stack

From repository root:

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

Services exposed:

- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### VPS Deployment

Follow `deployment/README.md` for end-to-end setup on Ubuntu 24.04 (`adminuser@113.30.191.89`), including Docker installation, environment configuration, migrations, optional systemd service, and firewall notes.

### Next Steps & Notes

- Provision HTTPS (e.g., Caddy, Nginx + Let's Encrypt) before exposing to production traffic.
- Implement production-grade Telegram login (current Android flow simulates credentials for demo).
- Integrate payout provider worker logic inside `app/tasks/payouts.py`.
- Add more comprehensive testing and CI/CD according to deployment policy.
