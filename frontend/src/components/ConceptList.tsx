import React from 'react';
import { Concept } from '../types/session';

interface ConceptListProps {
  concepts: Concept[];
}

export const ConceptList: React.FC<ConceptListProps> = ({ concepts }) => {
  return (
    <div>
      {concepts.map((concept, idx) => (
        <div key={idx} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '4px' }}>
          <h4>{concept.name}</h4>
          <p>{concept.explanation}</p>
        </div>
      ))}
    </div>
  );
};
