export interface Concept {
  name: string;
  explanation: string;
}

export interface Flashcard {
  question: string;
  answer: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface TranscriptSegment {
  text: string;
  start_ms?: number;
  end_ms?: number;
}

export interface StudyMaterials {
  summary: string;
  concepts: Concept[];
  flashcards: Flashcard[];
  quiz_questions: QuizQuestion[];
}

export interface Citation {
  text: string;
  start_ms?: number;
  end_ms?: number;
}

export interface Session {
  id: string;
  title: string;
  status: string;
  source_type: string;
  created_at: string;
  error_message?: string;
  transcript?: string;
  transcript_segments?: TranscriptSegment[];
  study_materials?: StudyMaterials;
}
