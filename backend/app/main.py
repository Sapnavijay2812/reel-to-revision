from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reel to Revision API", version="0.1.0")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logger.info(f"Starting up. DEMO_MODE: {settings.demo_mode}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down.")

# Routes will be imported below
from app.api import health, sessions
app.include_router(health.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
