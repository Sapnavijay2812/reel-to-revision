import json
import logging
from app.config import get_settings
from app.schemas import StudyMaterialsSchema, ConceptSchema, FlashcardSchema, QuizQuestionSchema
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()

def generate_study_materials(transcript: str) -> Optional[StudyMaterialsSchema]:
    """Generate study materials from transcript using Gemini or DEMO mode."""
    if settings.demo_mode:
        return _demo_study_materials()

    try:
        from vertexai.generative_models import GenerativeModel
        import vertexai

        vertexai.init(project=settings.google_cloud_project, location=settings.google_cloud_location)
        model = GenerativeModel(settings.gemini_model)

        with open("app/prompts/generate_study_materials.txt") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{transcript}", transcript)
        response = model.generate_content(prompt)

        # Parse JSON from response
        response_text = response.text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]

        data = json.loads(json_str)

        # Validate schema
        return StudyMaterialsSchema(
            summary=data["summary"],
            concepts=[ConceptSchema(**c) for c in data["concepts"]],
            flashcards=[FlashcardSchema(**f) for f in data["flashcards"]],
            quiz_questions=[QuizQuestionSchema(**q) for q in data["quiz_questions"]]
        )
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        return None

def _demo_study_materials() -> StudyMaterialsSchema:
    """Return demo study materials."""
    return StudyMaterialsSchema(
        summary="This is a sample summary of the educational content. It covers the main ideas in 2-3 sentences.",
        concepts=[
            ConceptSchema(
                name="Key Concept 1",
                explanation="This is an explanation of the first key concept from the transcript."
            ),
            ConceptSchema(
                name="Key Concept 2",
                explanation="This is an explanation of the second key concept."
            )
        ],
        flashcards=[
            FlashcardSchema(
                question="What is the main topic?",
                answer="The main topic is about educational content generation."
            ),
            FlashcardSchema(
                question="Give an example.",
                answer="An example would be summarizing a lecture into study materials."
            )
        ],
        quiz_questions=[
            QuizQuestionSchema(
                question="What does the content primarily discuss?",
                options=["Educational technology", "Video games", "Sports", "Cooking"],
                correct_index=0,
                explanation="The correct answer is Educational technology, as explained in the content."
            )
        ]
    )
