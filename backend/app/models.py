from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # 'transcript', 'video', 'demo'
    status = Column(String, nullable=False, default="processing")  # 'processing', 'completed', 'failed'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    error_message = Column(String, nullable=True)

    transcript = relationship("Transcript", back_populates="session", uselist=False, cascade="all, delete-orphan")
    study_materials = relationship("StudyMaterial", back_populates="session", uselist=False, cascade="all, delete-orphan")

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, unique=True)
    full_text = Column(Text, nullable=False)
    segments = Column(JSON, nullable=True)  # [{"text": "...", "start_ms": 0, "end_ms": 5000}]

    session = relationship("Session", back_populates="transcript")

class StudyMaterial(Base):
    __tablename__ = "study_materials"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    concepts = Column(JSON, nullable=False)  # [{"name": "...", "explanation": "..."}]
    flashcards = Column(JSON, nullable=False)  # [{"question": "...", "answer": "..."}]
    quiz_questions = Column(JSON, nullable=False)  # [{"question": "...", "options": [...], "correct_index": 0, "explanation": "..."}]

    session = relationship("Session", back_populates="study_materials")
