# Startup Digital Twin AI Backend

Production-ready FastAPI backend scaffold with PostgreSQL, SQLAlchemy ORM, Alembic migrations, Pydantic schemas, JWT authentication, bcrypt password hashing, and dotenv-based configuration.

## Structure

```text
backend/
  app/
    api/
    core/
    database/
    dependencies/
    middleware/
    models/
    schemas/
    services/
    utils/
    main.py
  alembic/
  alembic.ini
  requirements.txt
  .env
```

## Environment

Create or update `backend/.env`:

```env
APP_NAME="Startup Digital Twin AI"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=true
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/startup_digital_twin_ai"
SECRET_KEY="replace-with-a-long-random-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS="http://localhost:3000"
```

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`

Interactive docs are available at `/docs` outside production mode.
