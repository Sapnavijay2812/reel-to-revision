import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { Session } from '../types/session';
import { SummaryCard } from '../components/SummaryCard';
import { ConceptList } from '../components/ConceptList';
import { FlashcardViewer } from '../components/FlashcardViewer';
import { QuizPanel } from '../components/QuizPanel';
import { AskContentPanel } from '../components/AskContentPanel';

interface SessionPageProps {
  sessionId: string;
  onHome: () => void;
}

export const SessionPage: React.FC<SessionPageProps> = ({ sessionId, onHome }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await client.get(`/sessions/${sessionId}`);
        setSession(response.data);
      } catch (err) {
        setError('Failed to load session');
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [sessionId]);

  if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;
  if (!session) return <div style={{ padding: '2rem' }}>Session not found</div>;

  return (
    <div style={{ padding: '2rem' }}>
      <button onClick={onHome} style={{ marginBottom: '1rem' }}>← Back to Home</button>

      <h2>{session.title}</h2>
      {session.error_message && <p style={{ color: 'red' }}>Error: {session.error_message}</p>}

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc' }}>
        {['summary', 'concepts', 'flashcards', 'quiz', 'ask', 'transcript'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              marginRight: '0.5rem',
              padding: '0.5rem 1rem',
              background: activeTab === tab ? '#0066cc' : '#e0e0e0',
              color: activeTab === tab ? 'white' : 'black',
              border: 'none',
              borderRadius: '0'
            }}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div style={{ marginTop: '1rem' }}>
        {activeTab === 'summary' && session.study_materials && (
          <SummaryCard summary={session.study_materials.summary} />
        )}

        {activeTab === 'concepts' && session.study_materials && (
          <ConceptList concepts={session.study_materials.concepts} />
        )}

        {activeTab === 'flashcards' && session.study_materials && (
          <FlashcardViewer flashcards={session.study_materials.flashcards} />
        )}

        {activeTab === 'quiz' && session.study_materials && (
          <QuizPanel sessionId={sessionId} questions={session.study_materials.quiz_questions} />
        )}

        {activeTab === 'ask' && (
          <AskContentPanel sessionId={sessionId} />
        )}

        {activeTab === 'transcript' && (
          <pre style={{ background: '#f5f5f5', padding: '1rem', overflowX: 'auto' }}>
            {session.transcript}
          </pre>
        )}
      </div>
    </div>
  );
};
