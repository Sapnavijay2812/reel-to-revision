import React from 'react';
import { Citation } from '../types/session';

interface SourceCitationProps {
  citation: Citation;
  onClose: () => void;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ citation, onClose }) => {
  const timestamp = citation.start_ms ? `${Math.floor(citation.start_ms / 1000)}s` : 'N/A';

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        maxWidth: '600px',
        maxHeight: '80vh',
        overflowY: 'auto'
      }}>
        <h3>Source Citation</h3>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <div style={{ padding: '1rem', background: '#f5f5f5', borderRadius: '4px', marginBottom: '1rem' }}>
          <p style={{ fontStyle: 'italic' }}>"{citation.text}"</p>
        </div>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};
