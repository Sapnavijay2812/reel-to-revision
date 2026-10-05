import logging
from typing import List, Tuple
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def transcribe_audio(audio_path: str) -> Tuple[str, List[dict]]:
    """Transcribe audio using Google Cloud Speech-to-Text or DEMO mode."""
    if settings.demo_mode:
        return _demo_transcript()

    try:
        from google.cloud import speech_v1

        client = speech_v1.SpeechClient()

        # Read audio file
        with open(audio_path, 'rb') as f:
            audio_content = f.read()

        audio = speech_v1.RecognitionAudio(content=audio_content)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True
        )

        response = client.recognize(config=config, audio=audio)

        # Extract transcript and segments
        transcript = ""
        segments = []

        for result in response.results:
            for alternative in result.alternatives:
                transcript += alternative.transcript + " "

                # Extract word-level timing
                if alternative.words:
                    segment_start = None
                    segment_text = ""

                    for word_info in alternative.words:
                        word = word_info.word
                        start_time = int(word_info.start_time.total_seconds() * 1000)
                        end_time = int(word_info.end_time.total_seconds() * 1000)

                        if not segment_start:
                            segment_start = start_time

                        segment_text += word + " "

                        # Create segment every ~30 words or on sentence boundaries
                        if len(segment_text.split()) >= 30 or word.endswith(('.', '?', '!')):
                            segments.append({
                                "text": segment_text.strip(),
                                "start_ms": segment_start,
                                "end_ms": end_time
                            })
                            segment_text = ""
                            segment_start = None

                    # Add remaining text
                    if segment_text.strip():
                        segments.append({
                            "text": segment_text.strip(),
                            "start_ms": segment_start,
                            "end_ms": end_time
                        })

        return transcript.strip(), segments
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return _demo_transcript()

def _demo_transcript() -> Tuple[str, List[dict]]:
    """Return demo transcript with timestamps."""
    text = "The mitochondria is the powerhouse of the cell. It is responsible for producing energy through cellular respiration. This process converts glucose into ATP, which cells use for various functions."
    segments = [
        {
            "text": "The mitochondria is the powerhouse of the cell.",
            "start_ms": 0,
            "end_ms": 3000
        },
        {
            "text": "It is responsible for producing energy through cellular respiration.",
            "start_ms": 3000,
            "end_ms": 7000
        },
        {
            "text": "This process converts glucose into ATP, which cells use for various functions.",
            "start_ms": 7000,
            "end_ms": 12000
        }
    ]
    return text, segments
