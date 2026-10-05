import logging
from typing import List, Tuple
from app.config import get_settings
from app.schemas import CitationSchema

logger = logging.getLogger(__name__)
settings = get_settings()

def answer_question(question: str, transcript: str, segments: List[dict]) -> Tuple[str, List[CitationSchema]]:
    """Answer a question using Gemini and extract citations from transcript."""
    if settings.demo_mode:
        return _demo_answer()

    try:
        from vertexai.generative_models import GenerativeModel
        import vertexai

        vertexai.init(project=settings.google_cloud_project, location=settings.google_cloud_location)
        model = GenerativeModel(settings.gemini_model)

        with open("app/prompts/answer_question.txt") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{transcript}", transcript).replace("{question}", question)
        response = model.generate_content(prompt)
        answer = response.text.strip()

        # Extract citations
        citations = _extract_citations(answer, segments)

        return answer, citations
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        return "Error processing your question. Please try again.", []

def _extract_citations(answer: str, segments: List[dict]) -> List[CitationSchema]:
    """Find matching segments in transcript for answer."""
    citations = []

    # Simple keyword matching: find segments that overlap with answer
    answer_words = set(answer.lower().split())

    for segment in segments:
        segment_words = set(segment.get("text", "").lower().split())
        overlap = len(answer_words & segment_words)

        if overlap > 2:  # At least 3 words match
            citations.append(CitationSchema(
                text=segment["text"],
                start_ms=segment.get("start_ms"),
                end_ms=segment.get("end_ms")
            ))
            if len(citations) >= 2:
                break

    return citations

def _demo_answer() -> Tuple[str, List[CitationSchema]]:
    """Return demo answer and citations."""
    answer = "This is a demo answer generated from the sample transcript. It demonstrates how the Q&A feature works with citations."
    citations = [
        CitationSchema(
            text="This is a demo answer generated from the sample transcript.",
            start_ms=0,
            end_ms=5000
        )
    ]
    return answer, citations
