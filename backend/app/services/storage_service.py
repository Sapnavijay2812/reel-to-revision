import os
import logging
from datetime import datetime
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def save_upload(file_content: bytes, original_filename: str) -> str:
    """Save uploaded file to temp storage. Returns file path."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + original_filename.replace(' ', '_')

    file_path = os.path.join(settings.temp_upload_dir, filename)

    with open(file_path, 'wb') as f:
        f.write(file_content)

    return file_path

def cleanup_file(file_path: str):
    """Delete file after processing."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup {file_path}: {e}")
