import React from 'react';

interface SummaryCardProps {
  summary: string;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ summary }) => {
  return (
    <div style={{ padding: '1rem', borderRadius: '4px', background: '#f5f5f5' }}>
      <p>{summary}</p>
    </div>
  );
};
