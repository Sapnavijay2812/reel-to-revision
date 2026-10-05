import subprocess
import os
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def extract_audio(video_path: str) -> str:
    """Extract audio from video using FFmpeg. Returns path to audio file."""
    audio_path = video_path.replace('.mp4', '.wav').replace('.webm', '.wav').replace('.mov', '.wav')
    if not audio_path.endswith('.wav'):
        audio_path = audio_path + '.wav'

    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-q:a', '0',
            '-map', 'a',
            '-y',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise Exception(f"Failed to extract audio: {result.stderr}")

        if not os.path.exists(audio_path):
            raise Exception("Audio extraction failed: output file not created")

        return audio_path
    except FileNotFoundError:
        logger.error("FFmpeg not found. Install FFmpeg and add to PATH.")
        raise Exception("FFmpeg not installed. Video processing requires FFmpeg.")
    except Exception as e:
        logger.error(f"Audio extraction error: {e}")
        raise

def cleanup_temp_file(file_path: str):
    """Delete temporary file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup {file_path}: {e}")
