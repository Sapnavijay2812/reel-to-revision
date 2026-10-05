import React from 'react';
import { UploadPanel } from '../components/UploadPanel';

interface HomePageProps {
  onSessionCreated: (sessionId: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onSessionCreated }) => {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h2>Create Study Materials</h2>
      <p>Upload a video or paste a transcript to generate study materials</p>
      <UploadPanel onSessionCreated={onSessionCreated} />
    </div>
  );
};
