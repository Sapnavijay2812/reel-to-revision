import React, { useState } from 'react';
import client from '../api/client';
import { QuizQuestion } from '../types/session';

interface QuizPanelProps {
  sessionId: string;
  questions: QuizQuestion[];
}

export const QuizPanel: React.FC<QuizPanelProps> = ({ sessionId, questions }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<{ correct: boolean; explanation: string } | null>(null);
  const [loading, setLoading] = useState(false);

  if (questions.length === 0) return <p>No quiz questions</p>;

  const question = questions[currentIndex];

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await client.post(`/sessions/${sessionId}/quiz/submit`, {
        question_index: currentIndex,
        selected_option_index: selectedIndex
      });
      setFeedback({
        correct: response.data.correct,
        explanation: response.data.explanation
      });
    } catch (error) {
      setFeedback({ correct: false, explanation: 'Error submitting answer' });
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedIndex(null);
      setFeedback(null);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h3>{question.question}</h3>

      <div style={{ marginBottom: '2rem' }}>
        {question.options.map((option, idx) => (
          <label key={idx} style={{ display: 'block', marginBottom: '0.75rem' }}>
            <input
              type="radio"
              name="option"
              checked={selectedIndex === idx}
              onChange={() => setSelectedIndex(idx)}
              disabled={feedback !== null}
            />
            {' ' + option}
          </label>
        ))}
      </div>

      {!feedback ? (
        <button
          onClick={handleSubmit}
          disabled={selectedIndex === null || loading}
        >
          {loading ? 'Checking...' : 'Submit Answer'}
        </button>
      ) : (
        <div style={{
          padding: '1rem',
          background: feedback.correct ? '#c8e6c9' : '#ffcdd2',
          borderRadius: '4px',
          marginBottom: '1rem'
        }}>
          <p style={{ fontWeight: 'bold' }}>
            {feedback.correct ? '✓ Correct!' : '✗ Incorrect'}
          </p>
          <p>{feedback.explanation}</p>
          {currentIndex < questions.length - 1 && (
            <button onClick={handleNext} style={{ marginTop: '1rem' }}>
              Next Question
            </button>
          )}
          {currentIndex === questions.length - 1 && (
            <p style={{ marginTop: '1rem' }}>Quiz complete!</p>
          )}
        </div>
      )}

      <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '1rem' }}>
        Question {currentIndex + 1} / {questions.length}
      </p>
    </div>
  );
};
