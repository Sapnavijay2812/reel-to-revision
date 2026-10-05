from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ConceptSchema(BaseModel):
    name: str
    explanation: str

class FlashcardSchema(BaseModel):
    question: str
    answer: str

class QuizQuestionSchema(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str

class StudyMaterialsSchema(BaseModel):
    summary: str
    concepts: List[ConceptSchema]
    flashcards: List[FlashcardSchema]
    quiz_questions: List[QuizQuestionSchema]

class TranscriptSegmentSchema(BaseModel):
    text: str
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    title: str
    status: str
    source_type: str
    created_at: datetime
    error_message: Optional[str] = None

class FullSessionResponse(SessionResponse):
    transcript: Optional[str] = None
    transcript_segments: Optional[List[TranscriptSegmentSchema]] = None
    study_materials: Optional[StudyMaterialsSchema] = None

class CitationSchema(BaseModel):
    text: str
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None

class QuestionAnswerResponse(BaseModel):
    answer: str
    citations: List[CitationSchema]

class QuizSubmissionRequest(BaseModel):
    question_index: int
    selected_option_index: int

class QuizSubmissionResponse(BaseModel):
    correct: bool
    explanation: str
    correct_option_index: int

class QuestionRequest(BaseModel):
    question: str
