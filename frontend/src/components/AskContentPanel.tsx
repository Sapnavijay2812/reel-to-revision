import React, { useState } from 'react';
import client from '../api/client';
import { Citation } from '../types/session';
import { SourceCitation } from './SourceCitation';

interface AskContentPanelProps {
  sessionId: string;
}

export const AskContentPanel: React.FC<AskContentPanelProps> = ({ sessionId }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setAnswer('');
    setCitations([]);

    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    try {
      const response = await client.post(`/sessions/${sessionId}/questions`, {
        question: question.trim()
      });
      setAnswer(response.data.answer);
      setCitations(response.data.citations || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error processing question');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleAsk} style={{ marginBottom: '2rem' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the content..."
          style={{ width: '100%', padding: '0.75rem' }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: '0.5rem' }}>
          {loading ? 'Searching...' : 'Ask'}
        </button>
      </form>

      {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}

      {answer && (
        <div style={{ marginBottom: '2rem' }}>
          <h3>Answer</h3>
          <div style={{ padding: '1rem', background: '#f5f5f5', borderRadius: '4px', marginBottom: '1rem' }}>
            <p>{answer}</p>
          </div>

          {citations.length > 0 && (
            <div>
              <h4>Sources</h4>
              {citations.map((citation, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedCitation(citation)}
                  style={{
                    padding: '0.75rem',
                    background: '#e3f2fd',
                    border: '1px solid #0066cc',
                    borderRadius: '4px',
                    marginBottom: '0.5rem',
                    cursor: 'pointer'
                  }}
                >
                  <p style={{ fontSize: '0.85rem' }}>"{citation.text.slice(0, 100)}..."</p>
                  <p style={{ fontSize: '0.75rem', color: '#666' }}>Click to view full citation</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {selectedCitation && (
        <SourceCitation
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />
      )}
    </div>
  );
};
