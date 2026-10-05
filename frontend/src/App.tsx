import React, { useState, useEffect } from 'react';
import { AppHeader } from './components/AppHeader';
import { HomePage } from './pages/HomePage';
import { SessionPage } from './pages/SessionPage';
import client from './api/client';

export default function App() {
  const [demoMode, setDemoMode] = useState(false);
  const [currentPage, setCurrentPage] = useState('home');
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    client.get('/health')
      .then((res) => setDemoMode(res.data.demo_mode))
      .catch(() => setDemoMode(true));
  }, []);

  const goToSession = (id: string) => {
    setSessionId(id);
    setCurrentPage('session');
  };

  const goHome = () => {
    setCurrentPage('home');
    setSessionId(null);
  };

  return (
    <>
      <AppHeader demoMode={demoMode} />
      <main>
        {currentPage === 'home' ? (
          <HomePage onSessionCreated={goToSession} />
        ) : (
          <SessionPage sessionId={sessionId!} onHome={goHome} />
        )}
      </main>
    </>
  );
}
