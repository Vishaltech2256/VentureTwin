from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.database.database import engine, get_db, Base
import app.models.user
import app.models.startup_profile
import app.models.prediction
import app.models.ai_suggestion
import app.models.report

from app.api.router import api_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Starting up Startup Digital Twin AI Backend...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not auto-create tables: {e}")
    yield
    # Shutdown event
    logger.info("Shutting down Startup Digital Twin AI Backend...")

app = FastAPI(
    title="Startup Digital Twin AI",
    version="1.0.0",
    lifespan=lifespan
)

# Set CORS enabled origins
# Note: When allow_credentials=True, browsers reject wildcard '*' on requests with credentials.
# allow_origin_regex ensures the caller's origin is dynamically validated and reflected.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Startup Digital Twin AI Backend is running"}

@app.get("/health")
@app.get("/api/health")
def health_check():
    """
    Health check endpoint that verifies the database connection.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")

# Register all API routers
if api_router:
    app.include_router(api_router, prefix="/api")
else:
    logger.warning("api_router not found. Ensure you have an api router to include.")

