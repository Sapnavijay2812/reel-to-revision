import React, { useState } from 'react';
import client from '../api/client';

interface UploadPanelProps {
  onSessionCreated: (sessionId: string) => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ onSessionCreated }) => {
  const [title, setTitle] = useState('');
  const [transcript, setTranscript] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useVideo, setUseVideo] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!useVideo && !transcript.trim()) {
      setError('Please paste a transcript or select a video');
      return;
    }

    if (useVideo && !videoFile) {
      setError('Please select a video file');
      return;
    }

    setLoading(true);
    try {
      if (useVideo && videoFile) {
        const formData = new FormData();
        formData.append('title', title || videoFile.name);
        formData.append('video', videoFile);

        const response = await client.post('/sessions', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        onSessionCreated(response.data.id);
      } else {
        const response = await client.post('/sessions', {
          title: title || 'Untitled Session',
          transcript: transcript.trim()
        });
        onSessionCreated(response.data.id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creating session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '600px', margin: '0 auto', padding: '1rem' }}>
      <div style={{ marginBottom: '1rem' }}>
        <label>
          Session Title (optional)
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Biology Lecture"
            style={{ display: 'block', width: '100%', marginTop: '0.5rem' }}
          />
        </label>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <div style={{ marginBottom: '0.5rem' }}>
          <label style={{ marginRight: '1rem' }}>
            <input
              type="radio"
              checked={!useVideo}
              onChange={() => setUseVideo(false)}
            />
            {' '}Paste Transcript
          </label>
          <label>
            <input
              type="radio"
              checked={useVideo}
              onChange={() => setUseVideo(true)}
            />
            {' '}Upload Video
          </label>
        </div>
      </div>

      {!useVideo && (
        <div style={{ marginBottom: '1rem' }}>
          <label>
            Paste Transcript
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste your transcript here..."
              rows={10}
              style={{ display: 'block', width: '100%', marginTop: '0.5rem' }}
            />
          </label>
        </div>
      )}

      {useVideo && (
        <div style={{ marginBottom: '1rem' }}>
          <label>
            Select Video File
            <input
              type="file"
              accept="video/mp4,video/webm,video/quicktime,.mov"
              onChange={(e) => setVideoFile(e.files?.[0] || null)}
              style={{ display: 'block', marginTop: '0.5rem' }}
            />
          </label>
          {videoFile && (
            <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
              Selected: {videoFile.name} ({(videoFile.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          )}
          <p style={{ fontSize: '0.75rem', color: '#999' }}>
            Supported: MP4, WebM, MOV (requires Google Cloud Speech-to-Text in non-DEMO mode)
          </p>
        </div>
      )}

      {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Start Processing'}
      </button>
    </form>
  );
};
