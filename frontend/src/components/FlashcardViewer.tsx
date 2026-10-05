import React, { useState } from 'react';
import { Flashcard } from '../types/session';

interface FlashcardViewerProps {
  flashcards: Flashcard[];
}

export const FlashcardViewer: React.FC<FlashcardViewerProps> = ({ flashcards }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  if (flashcards.length === 0) return <p>No flashcards</p>;

  const card = flashcards[currentIndex];

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div
        onClick={() => setFlipped(!flipped)}
        style={{
          padding: '2rem',
          background: flipped ? '#e3f2fd' : '#fff3e0',
          border: '2px solid #0066cc',
          borderRadius: '8px',
          minHeight: '200px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          cursor: 'pointer',
          marginBottom: '2rem'
        }}
      >
        <div>
          <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: '1rem' }}>
            {flipped ? 'Answer' : 'Question'}
          </p>
          <p style={{ fontSize: '1.2rem' }}>
            {flipped ? card.answer : card.question}
          </p>
          <p style={{ fontSize: '0.75rem', color: '#999', marginTop: '1rem' }}>
            Click to {flipped ? 'show question' : 'reveal answer'}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <button
          onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
          disabled={currentIndex === 0}
        >
          ← Previous
        </button>

        <span style={{ fontSize: '0.9rem', color: '#666' }}>
          {currentIndex + 1} / {flashcards.length}
        </span>

        <button
          onClick={() => setCurrentIndex(Math.min(flashcards.length - 1, currentIndex + 1))}
          disabled={currentIndex === flashcards.length - 1}
        >
          Next →
        </button>
      </div>
    </div>
  );
};
