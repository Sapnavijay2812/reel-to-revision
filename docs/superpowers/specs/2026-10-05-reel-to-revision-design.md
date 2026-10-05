# Reel to Revision: MVP Design

**Date:** 2026-10-05  
**Project:** Educational content transformer: upload videos/transcripts, generate study materials  
**Scope:** Complete MVP with 6 study material types, DEMO mode, SQLite persistence  

---

## 1. Problem & Success Criteria

### Intent
Users upload educational videos or paste transcripts. The app instantly generates structured study materials: summaries, key concepts, flashcards, quizzes, Q&A with citations, and transcript references. The main value is time-saving and grounding—all answers cite the actual content, never hallucinate.

### Success Criteria
- Complete user flow works: paste transcript → review all 6 study material types → ask questions → take quiz
- App runs locally in DEMO mode without Google Cloud credentials
- All AI-generated content is validated (schema checked, not silently invalid)
- Q&A answers are grounded in transcript, citations are correct
- Code is testable and modular (services, schemas, clear boundaries)
- Documentation explains setup, DEMO mode, and GCP configuration

### Constraints
- MVP, not production: focus on core flow, defer advanced features (user accounts, export, sharing)
- Sessions persist in SQLite; no session sync across tabs/devices needed
- DEMO mode must be realistic but clearly labeled
- Video transcription skipped initially; paste flow works first

---

## 2. System Architecture

### High-Level Data Flow

```
User Uploads/Pastes
        ↓
Session Created (SQLite)
        ↓
Gemini Generates Materials (or DEMO mock)
        ↓
Study Materials Stored
        ↓
Frontend Fetches & Displays
        ↓
User Asks Questions / Takes Quiz
        ↓
Gemini Grounds Answers in Transcript
        ↓
Citations Extracted & Returned
```

### Tech Stack

| Layer | Tech | Rationale |
|-------|------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Modern, fast builds, type safety |
| **Backend** | Python 3.9+ + FastAPI | Async, auto-docs, Pydantic validation |
| **Database** | SQLite | Local dev, no external service, easy snapshots |
| **AI** | Google Cloud Gemini (via Vertex AI) | State-of-art, grounded outputs, JSON mode |
| **Audio** | FFmpeg | Video → audio, reliable, widely available |
| **Transcription** | Google Cloud Speech-to-Text | Accurate, handles timestamps |
| **Storage** | Google Cloud Storage (configurable) | Scalable, but local temp files in dev |

### Project Structure

```
reel-to-revision/
├── README.md                 # Setup, local dev, GCP config, limitations
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── frontend/                 # React app
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   ├── client.ts       # Axios wrapper
│       │   └── sessions.ts     # Session CRUD, questions, quiz
│       ├── components/
│       │   ├── AppHeader.tsx
│       │   ├── UploadPanel.tsx
│       │   ├── ProcessingStatus.tsx
│       │   ├── SummaryCard.tsx
│       │   ├── ConceptList.tsx
│       │   ├── FlashcardViewer.tsx
│       │   ├── QuizPanel.tsx
│       │   ├── AskContentPanel.tsx
│       │   ├── SourceCitation.tsx
│       │   └── ErrorMessage.tsx
│       ├── pages/
│       │   ├── HomePage.tsx    # Paste/upload form
│       │   └── SessionPage.tsx # Study materials tabs
│       ├── types/
│       │   └── session.ts      # TypeScript interfaces
│       └── styles/
│           └── global.css
│
└── backend/                  # FastAPI app
    ├── requirements.txt
    ├── Dockerfile
    ├── app/
    │   ├── main.py             # FastAPI app, routes, startup
    │   ├── config.py           # Settings (GCP, DEMO mode, DB path)
    │   ├── database.py         # SQLAlchemy setup
    │   ├── models.py           # ORM models
    │   ├── schemas.py          # Pydantic request/response
    │   ├── api/
    │   │   ├── health.py       # GET /health
    │   │   └── sessions.py     # All session endpoints
    │   ├── services/
    │   │   ├── video_service.py           # FFmpeg audio extraction
    │   │   ├── transcription_service.py   # GCP Speech-to-Text or mock
    │   │   ├── gemini_service.py          # Gemini API calls + JSON parsing
    │   │   ├── study_material_service.py  # Generate materials from transcript
    │   │   └── storage_service.py         # GCS or local temp file handling
    │   ├── prompts/
    │   │   ├── generate_study_materials.txt
    │   │   └── answer_question.txt
    │   └── utils/
    │       └── timestamps.py    # Segment extraction, citation helpers
    │
    └── tests/
        ├── test_health.py
        ├── test_sessions.py
        ├── test_gemini_parsing.py
        └── test_study_materials.py
```

---

## 3. Frontend Architecture

### Pages & Components

#### HomePage
- Header with app title + demo badge (if DEMO mode)
- Two input methods (tabs):
  - **Upload video:** file input accepting mp4, webm, mov, etc.
  - **Paste transcript:** textarea for raw text
- "Start Processing" button (disabled if both empty)
- Validation: show errors inline (file too large, unsupported format, empty text)
- After submission: redirect to `/sessions/{id}` with loading state

#### SessionPage
- Header: session title, source type, processing status
- Tabs or vertical layout:
  1. **Summary:** read-only text card
  2. **Key Concepts:** list of concept boxes (name + explanation)
  3. **Flashcards:** single card with flip toggle, prev/next buttons
  4. **Quiz:** one question at a time, radio options, submit button, explanation after selection
  5. **Ask:** textarea input + search results (answer + citations); citation links open transcript modal
  6. **Transcript:** full text with timestamps, highlighted when cited

#### Components
- **SourceCitation:** modal/drawer showing transcript excerpt (context lines around match) + timestamp link
- **ProcessingStatus:** spinner + "Generating materials..." until status: completed
- **ErrorMessage:** toast or inline error with retry option
- **Loading skeleton:** placeholder blocks while data loads

### State Management & API Calls
- Use React hooks (useState, useEffect) for simplicity (no Redux needed for MVP)
- API client (axios or fetch wrapper) handles:
  - Session CRUD: create, fetch, list
  - Question submission: POST with transcript context
  - Quiz: submit answer, get feedback
  - Error handling: show toast on 4xx/5xx
- Poll `/api/sessions/{id}` every 2 seconds if status is "processing" (or use websocket if backend supports)

### Styling & UX
- Clean, minimal design (Tailwind or plain CSS)
- Dark mode support (prefers-color-scheme)
- Responsive: mobile-friendly (flexbox, media queries)
- Loading states: skeleton loaders, spinner buttons
- Error states: toast messages, inline validation
- Demo mode badge: prominent banner at top

---

## 4. Backend API & Database

### REST Endpoints

#### `GET /api/health`
**Response:**
```json
{
  "status": "ok",
  "demo_mode": false,
  "version": "0.1.0"
}
```
- Always returns 200; demo_mode bool lets frontend show banner

#### `POST /api/sessions`
**Request:**
```json
{
  "title": "Biology 101 Lecture",
  "transcript": "The mitochondria is...",  // Either this
  "video": <File>                          // Or this; multipart/form-data
}
```
**Validation:**
- Reject if both transcript and video missing (400)
- Reject if transcript empty (400)
- Reject if video > MAX_UPLOAD_MB (413)
- Reject if video format unsupported (400)

**Response:**
```json
{
  "session_id": "abc123",
  "title": "Biology 101 Lecture",
  "status": "processing",  // or "completed" for transcript-paste
  "source_type": "transcript",
  "created_at": "2026-10-05T12:00:00Z"
}
```
**Behavior:**
- Create session record
- For transcript: save to DB, immediately generate materials (or queue async job)
- For video: extract audio with FFmpeg, transcribe with Speech-to-Text, generate materials
- Set status to "completed" when done; "failed" if any step fails
- Return error_message if processing failed

#### `GET /api/sessions/{session_id}`
**Response:**
```json
{
  "id": "abc123",
  "title": "Biology 101 Lecture",
  "status": "completed",
  "source_type": "transcript",
  "transcript": "The mitochondria is...",
  "transcript_segments": [
    { "text": "The mitochondria...", "start_ms": 0, "end_ms": 5000 }
  ],
  "study_materials": {
    "summary": "A high-level overview of mitochondrial function...",
    "concepts": [
      { "name": "Mitochondria", "explanation": "The powerhouse of the cell..." }
    ],
    "flashcards": [
      { "question": "What is the mitochondria?", "answer": "The powerhouse..." }
    ],
    "quiz_questions": [
      {
        "question": "What does the mitochondria do?",
        "options": ["A) Energy production", "B) Digestion", ...],
        "correct_index": 0,
        "explanation": "The mitochondria produces ATP..."
      }
    ]
  },
  "created_at": "2026-10-05T12:00:00Z",
  "error_message": null
}
```

#### `POST /api/sessions/{session_id}/questions`
**Request:**
```json
{
  "question": "What is the mitochondria's main function?"
}
```
**Response:**
```json
{
  "answer": "The mitochondria is responsible for energy production...",
  "citations": [
    {
      "text": "The mitochondria is the powerhouse of the cell, producing ATP...",
      "start_ms": 1000,
      "end_ms": 5000
    }
  ]
}
```
**Behavior:**
- Pass user question + full transcript to Gemini with prompt: "Answer only using this transcript. If the answer is not found, say so."
- Parse response for answer + relevant transcript segments
- Extract citations: find matching text in transcript_segments, include timestamps
- If not found: return `{ answer: "I couldn't find that in the transcript.", citations: [] }`

#### `POST /api/sessions/{session_id}/quiz/submit`
**Request:**
```json
{
  "question_index": 0,
  "selected_option_index": 1
}
```
**Response:**
```json
{
  "correct": false,
  "explanation": "The correct answer is A) Energy production. The mitochondria...",
  "correct_option_index": 0
}
```
**Behavior:**
- Fetch quiz question from study_materials
- Compare selected_option_index to correct_index
- Return correctness + explanation

### Database Schema

```sql
-- Sessions
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,  -- 'transcript', 'video', 'demo'
  status TEXT NOT NULL,        -- 'processing', 'completed', 'failed'
  created_at TIMESTAMP NOT NULL,
  error_message TEXT
);

-- Transcripts
CREATE TABLE transcripts (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL UNIQUE,
  full_text TEXT NOT NULL,
  segments JSON,  -- [{"text": "...", "start_ms": 0, "end_ms": 5000}]
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Study Materials
CREATE TABLE study_materials (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL UNIQUE,
  summary TEXT NOT NULL,
  concepts JSON,  -- [{"name": "...", "explanation": "..."}]
  flashcards JSON,  -- [{"question": "...", "answer": "..."}]
  quiz_questions JSON,  -- [{"question": "...", "options": [...], "correct_index": 0, "explanation": "..."}]
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

### Error Handling

| Scenario | Status | Response |
|----------|--------|----------|
| No transcript or video | 400 | `{ "detail": "Provide either transcript or video" }` |
| Transcript empty | 400 | `{ "detail": "Transcript cannot be empty" }` |
| Video too large | 413 | `{ "detail": "File exceeds MAX_UPLOAD_MB" }` |
| Unsupported video format | 400 | `{ "detail": "Unsupported format. Supported: mp4, webm, mov" }` |
| Gemini returns invalid JSON | 500 | Session saved with `status: failed`, `error_message: "Failed to parse study materials"` |
| Missing transcripts in GET | 404 | `{ "detail": "Session not found" }` |
| GCP API unavailable | 500 | In non-DEMO: error. In DEMO: fallback to mock data |

---

## 5. AI & Content Generation

### Gemini Integration

**Study Material Generation Prompt:**
- Input: full transcript
- Output: JSON with summary, concepts, flashcards, quiz_questions (schema below)
- Validation: before saving, parse JSON; reject if malformed
- DEMO mode: return hardcoded realistic sample output

**JSON Schema (Gemini's response):**
```json
{
  "summary": "string (2-3 sentences)",
  "concepts": [
    {
      "name": "string",
      "explanation": "string (1-2 sentences)"
    }
  ],
  "flashcards": [
    {
      "question": "string",
      "answer": "string"
    }
  ],
  "quiz_questions": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_index": 0,
      "explanation": "string"
    }
  ]
}
```

### Q&A Answering Prompt
- Input: user question + full transcript
- Instruction: "Answer ONLY using the provided transcript. If the answer is not in the transcript, respond with 'I could not find the answer in the transcript.' Do not add outside knowledge."
- Output: plain text answer (not JSON)
- Post-processing: search transcript for relevant segments, extract citations with timestamps

### Citation Extraction
- After Gemini returns answer, search for key phrases from the answer in transcript_segments
- Return segment(s) with matching text + timestamps
- If no exact match: use semantic similarity or return no citations with disclaimer

### DEMO Mode
- `/api/health` returns `demo_mode: true` before any credentials configured
- `POST /api/sessions` with transcript: return pre-made study materials (hardcoded realistic example)
- `POST /api/sessions/{id}/questions`: return pre-made Q&A + citations
- Frontend shows banner: "Demo mode: Using sample data. Configure Google Cloud credentials to use real AI."

---

## 6. Video Processing (Phase 5)

### Video Upload & Transcription
- Accept mp4, webm, mov (validate MIME type)
- Use FFmpeg to extract audio: `ffmpeg -i video.mp4 -q:a 0 -map a audio.wav`
- Store temp audio file in `/tmp` or configurable directory
- Call Google Cloud Speech-to-Text: `speech_v1.SpeechClient.recognize(config, audio)`
- Receive transcript + word-level timestamps
- Group into sentence segments (or use utterance breaks)
- Save to transcript table with timestamps
- Clean up temp files after successful save

### Transcript Segmentation
- Speech-to-Text returns word-level results with timestamps
- Group into sentences or short segments (30-60 words each)
- Store as: `[{ "text": "...", "start_ms": 0, "end_ms": 5000 }]`
- Use for citation links: when user clicks citation, jump to segment and highlight

---

## 7. Configuration & Environment

### `.env.example`
```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=my-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_CLOUD_STORAGE_BUCKET=my-bucket-name

# Gemini
GEMINI_MODEL=gemini-2.0-flash

# Database
DATABASE_URL=sqlite:///./sessions.db

# App
DEMO_MODE=true
MAX_UPLOAD_MB=100
FRONTEND_ORIGIN=http://localhost:5173
LOG_LEVEL=INFO
```

### Startup Behavior
- If `DEMO_MODE=true` or GCP credentials missing: set `demo_mode=true` in health endpoint
- If `GOOGLE_APPLICATION_CREDENTIALS` invalid or unreachable: log warning, fall back to DEMO mode
- Initialize SQLite DB on startup (create tables if missing)
- Log startup config (not secrets)

---

## 8. Testing Strategy

### Backend Tests (pytest)
- **test_health.py:** health endpoint returns status + demo_mode flag
- **test_sessions.py:** 
  - POST session with transcript: creates record, returns ID
  - POST with missing transcript: returns 400
  - GET session: fetches full record
  - POST question: returns answer + citations
  - POST quiz: returns correctness + explanation
- **test_gemini_parsing.py:** 
  - Valid JSON from Gemini: parses correctly
  - Invalid JSON: gracefully fails, returns error
- **test_study_materials.py:** 
  - Citation extraction: finds relevant segments
  - No match: returns empty citations

### Frontend Tests (React Testing Library, optional for MVP)
- HomePage: form validation, disabled button when empty
- SessionPage: tabs switch correctly, data displays
- Manual testing: complete flow (paste → review → ask → quiz)

### Integration
- LocalStack/fake GCS for testing without real GCP
- Mock Gemini responses in test suite
- SQLite test database (in-memory or temp file)

---

## 9. Error Handling & Edge Cases

| Scenario | Handling |
|----------|----------|
| Gemini returns non-JSON response | Log error, set session status=failed, show user error message |
| Gemini JSON missing required fields | Validate schema, reject if incomplete, set status=failed |
| User asks question not in transcript | Return "I couldn't find that" + empty citations |
| Q&A answer is extremely long | Return full answer; frontend can truncate in UI if needed |
| Video with no audio track | Reject with 400 "Video must contain audio" |
| Transcript with zero content for Q&A | Return "Transcript is empty" when user asks question |
| GCP API rate limit hit | Return 429; frontend can show "Please try again in a moment" |
| Session not found | Return 404 "Session not found" |

---

## 10. Implementation Sequence

### Phase 1: App Shell & Health (Day 1)
- Init monorepo, scaffold frontend + backend
- FastAPI `/api/health` endpoint
- Frontend App.tsx with routing (HomePage, SessionPage)
- Deploy frontend dev server (Vite)

### Phase 2: Transcript Input & Persistence (Day 1-2)
- `POST /api/sessions` accepts transcript text
- SQLite setup, session + transcript tables
- `GET /api/sessions/{id}`
- HomePage form + validation
- SessionPage skeleton (tabs, empty states)

### Phase 3: Study Material Generation & Q&A (Day 2-3)
- Integrate Gemini (or mock in DEMO mode)
- `study_material_service.py` generates materials from transcript
- Store in study_materials table
- Display in SessionPage (summary, concepts, flashcards)
- `POST /api/sessions/{id}/questions` + citation extraction
- AskContentPanel + SourceCitation modal

### Phase 4: Flashcards & Quiz (Day 3)
- FlashcardViewer component (flip, navigation)
- QuizPanel component (single question, options, feedback)
- `POST /api/sessions/{id}/quiz/submit` endpoint

### Phase 5: Video Upload & Transcription (Day 4)
- UploadPanel for video files
- FFmpeg audio extraction
- Google Cloud Speech-to-Text integration (or mock)
- Segment transcript with timestamps

### Phase 6: Tests, Documentation, Polish (Day 4-5)
- Pytest test suite for critical paths
- README: setup, DEMO mode, GCP config, limitations
- Error handling, logging, edge cases
- Frontend polish: dark mode, responsive, loading states

---

## 11. Known Limitations & Future Work

**MVP Limitations:**
- No user accounts or session sharing
- No export (PDF, Anki, etc.)
- No video seeking with transcript sync
- Flashcard/quiz answers not persisted (frontend only)
- No speech recognition for spoken questions
- No offline mode

**Future:**
- User auth + session library
- Export study materials
- Advanced filtering (by concept, difficulty)
- Spaced repetition algorithm
- Video subtitle generation
- Collaborative study groups

---

## 12. Success Metrics

- [x] App runs locally without GCP credentials (DEMO mode)
- [x] Complete flow works: paste transcript → view all 6 materials → ask questions → take quiz
- [x] Q&A answers cite actual transcript, no hallucination
- [x] Sessions persist across app restarts
- [x] Code is modular, testable, well-documented
- [x] README explains setup and limitations clearly

---

**Status:** Design approved by user. Ready for implementation planning.
