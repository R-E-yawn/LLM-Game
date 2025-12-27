import { useState, useEffect } from 'react';
import Scenario from './components/Scenario';
import Stats from './components/Stats';
import Chat from './components/Chat';
import { gameAPI } from './services/api';
import './App.css';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [scenario, setScenario] = useState('');
  const [stats, setStats] = useState({ health: 100, coins: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = async () => {
    setLoading(true);
    setError(null);
    
    const defaultScenario = 
      "You are an adventurer in a fantasy world. You wake up in a small village with 100 health and 0 coins. " +
      "Your goal is to explore, complete quests, and survive. What would you like to do?";

    try {
      const response = await gameAPI.startGame(defaultScenario);
      setSessionId(response.session_id);
      setScenario(response.scenario);
      setStats(response.stats || { health: 100, coins: 0 });
    } catch (err) {
      console.error('Failed to start game:', err);
      setError('Failed to start game. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleStateUpdate = (newStats) => {
    setStats(newStats);
  };

  if (loading && !sessionId) {
    return (
      <div className="app-container">
        <div className="loading">Starting your adventure...</div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Impostor.AI</h1>
        <button className="new-game-button" onClick={startNewGame}>
          New Game
        </button>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="game-content">
        <div className="game-info">
          <Scenario scenario={scenario} />
          <Stats stats={stats} />
        </div>
        <div className="game-chat">
          <Chat sessionId={sessionId} onStateUpdate={handleStateUpdate} />
        </div>
      </div>
    </div>
  );
}

export default App;
