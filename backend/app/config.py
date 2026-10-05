from pydantic_settings import BaseSettings
from functools import lru_cache
import tempfile
import os

class Settings(BaseSettings):
    database_url: str = "sqlite:///./sessions.db"
    demo_mode: bool = True
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    google_application_credentials: str = ""
    google_cloud_storage_bucket: str = ""
    gemini_model: str = "gemini-2.0-flash"
    max_upload_mb: int = 100
    frontend_origin: str = "http://localhost:5173"
    log_level: str = "INFO"
    temp_upload_dir: str = tempfile.gettempdir()

    class Config:
        env_file = ".env"

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure temp dir exists
        os.makedirs(self.temp_upload_dir, exist_ok=True)
        # If GCP creds missing, force demo mode
        if not self.google_application_credentials:
            self.demo_mode = True

@lru_cache()
def get_settings():
    return Settings()
