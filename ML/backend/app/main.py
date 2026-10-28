from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.database.database import engine, get_db
# Assuming there is a central router in app.api or we import routers individually.
# If an api router doesn't exist yet, you can adjust this import.
try:
    from app.api.router import api_router
except ImportError:
    api_router = None

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Starting up Startup Digital Twin AI Backend...")
    # Add any startup logic here (e.g., initial cache loading, etc.)
    yield
    # Shutdown event
    logger.info("Shutting down Startup Digital Twin AI Backend...")
    # Add any shutdown logic here

app = FastAPI(
    title="Startup Digital Twin AI",
    version="1.0.0",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this using settings.ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Startup Digital Twin AI Backend is running"}

@app.get("/health")
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

