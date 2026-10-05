import React from 'react';

interface AppHeaderProps {
  demoMode?: boolean;
}

export const AppHeader: React.FC<AppHeaderProps> = ({ demoMode }) => {
  return (
    <header style={{ padding: '1rem', borderBottom: '1px solid #cccccc' }}>
      <h1>Reel to Revision</h1>
      {demoMode && (
        <p style={{ fontSize: '0.85rem', color: '#666' }}>
          Demo mode: Using sample data. Configure Google Cloud credentials to use real AI.
        </p>
      )}
    </header>
  );
};
