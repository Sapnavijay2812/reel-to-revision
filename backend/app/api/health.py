from fastapi import APIRouter
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    version: str

@router.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        demo_mode=settings.demo_mode,
        version="0.1.0"
    )
