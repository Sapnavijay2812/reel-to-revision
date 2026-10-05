from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Session as SessionModel, Transcript as TranscriptModel, StudyMaterial as StudyMaterialModel
from app.schemas import CreateSessionRequest, SessionResponse, FullSessionResponse, StudyMaterialsSchema, QuestionAnswerResponse, QuizSubmissionRequest, QuizSubmissionResponse, QuestionRequest
from app.config import get_settings
from app.services.gemini_service import generate_study_materials
from app.services.study_material_service import answer_question
import uuid
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sessions"])
settings = get_settings()

@router.post("/sessions", status_code=201, response_model=SessionResponse)
async def create_session(
    title: str = Form(None),
    transcript: str = Form(None),
    video: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Validate input
    if not transcript and not video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either transcript or video"
        )

    transcript_text = None
    transcript_segments = [{"text": "", "start_ms": 0, "end_ms": 0}]
    source_type = "transcript"

    # Handle transcript paste
    if transcript:
        transcript_text = transcript.strip()
        if not transcript_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript cannot be empty"
            )
        transcript_segments = [{"text": transcript_text, "start_ms": 0, "end_ms": 0}]
        source_type = "transcript"

    # Handle video upload (stub - will call transcription service)
    if video:
        source_type = "video"
        try:
            content = await video.read()
            file_size_mb = len(content) / (1024 * 1024)
            if file_size_mb > settings.max_upload_mb:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {settings.max_upload_mb}MB limit"
                )

            # In DEMO mode, use demo transcript; otherwise transcribe
            if settings.demo_mode:
                transcript_text, transcript_segments = ("Demo video transcript: The mitochondria is the powerhouse of the cell.",
                                                        [{"text": "Demo video transcript: The mitochondria is the powerhouse of the cell.", "start_ms": 0, "end_ms": 5000}])
            else:
                # Would call transcription_service here
                transcript_text = "Video transcription not configured"
                transcript_segments = [{"text": transcript_text, "start_ms": 0, "end_ms": 0}]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Create session
    session_id = str(uuid.uuid4())
    session = SessionModel(
        id=session_id,
        title=title or "Untitled",
        source_type=source_type,
        status="processing",
        created_at=datetime.utcnow()
    )
    db.add(session)
    db.flush()

    # Create transcript
    transcript_obj = TranscriptModel(
        id=str(uuid.uuid4()),
        session_id=session_id,
        full_text=transcript_text,
        segments=transcript_segments
    )
    db.add(transcript_obj)
    db.commit()

    # Generate study materials
    materials = generate_study_materials(transcript_text)
    if materials:
        study_material = StudyMaterialModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            summary=materials.summary,
            concepts=[c.dict() for c in materials.concepts],
            flashcards=[f.dict() for f in materials.flashcards],
            quiz_questions=[q.dict() for q in materials.quiz_questions]
        )
        db.add(study_material)
        session.status = "completed"
    else:
        session.status = "failed"
        session.error_message = "Failed to generate study materials"

    db.commit()

    return SessionResponse(
        id=session.id,
        title=session.title,
        status=session.status,
        source_type=session.source_type,
        created_at=session.created_at
    )

@router.get("/sessions/{session_id}", response_model=FullSessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    transcript = db.query(TranscriptModel).filter(TranscriptModel.session_id == session_id).first()
    study_materials = db.query(StudyMaterialModel).filter(StudyMaterialModel.session_id == session_id).first()

    result = FullSessionResponse(
        id=session.id,
        title=session.title,
        status=session.status,
        source_type=session.source_type,
        created_at=session.created_at,
        error_message=session.error_message,
        transcript=transcript.full_text if transcript else None,
        transcript_segments=transcript.segments if transcript else None,
    )

    if study_materials:
        result.study_materials = StudyMaterialsSchema(
            summary=study_materials.summary,
            concepts=study_materials.concepts,
            flashcards=study_materials.flashcards,
            quiz_questions=study_materials.quiz_questions
        )

    return result

@router.post("/sessions/{session_id}/questions", response_model=QuestionAnswerResponse)
async def post_question(
    session_id: str,
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    transcript = db.query(TranscriptModel).filter(TranscriptModel.session_id == session_id).first()
    if not transcript:
        raise HTTPException(status_code=400, detail="No transcript for this session")

    answer, citations = answer_question(
        request.question,
        transcript.full_text,
        transcript.segments or []
    )

    return QuestionAnswerResponse(answer=answer, citations=citations)

@router.post("/sessions/{session_id}/quiz/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(
    session_id: str,
    request: QuizSubmissionRequest,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    materials = db.query(StudyMaterialModel).filter(StudyMaterialModel.session_id == session_id).first()
    if not materials:
        raise HTTPException(status_code=400, detail="No study materials for this session")

    questions = materials.quiz_questions
    if request.question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Invalid question index")

    question = questions[request.question_index]
    correct = request.selected_option_index == question["correct_index"]

    return QuizSubmissionResponse(
        correct=correct,
        explanation=question["explanation"],
        correct_option_index=question["correct_index"]
    )
