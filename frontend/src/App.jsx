import { useState, useEffect } from 'react';
import Scenario from './components/Scenario';
import Stats from './components/Stats';
import Chat from './components/Chat';
import ChatSelector from './components/ChatSelector';
import ImpostorSelection from './components/ImpostorSelection';
import ApiKeyInput from './components/ApiKeyInput';
import { gameAPI } from './services/api';
import './App.css';

function App() {
  // Game initialization state
  const [gamePhase, setGamePhase] = useState('api-key'); // 'api-key', 'loading', 'playing', 'selecting', 'result'
  const [apiKey, setApiKey] = useState('');
  const [gameId, setGameId] = useState(null);
  const [initError, setInitError] = useState(null);
  
  // Game state
  const [activeChat, setActiveChat] = useState('yellow');
  const [questionsLeft, setQuestionsLeft] = useState(30);
  const [chatHistories, setChatHistories] = useState({
    red: [],
    yellow: [],
    green: [],
    blue: [],
  });
  
  // Result state
  const [gameResult, setGameResult] = useState(null);
  const [actualImpostor, setActualImpostor] = useState(null);

  // Handle API key submission and game initialization
  const handleApiKeySubmit = async (key) => {
    setApiKey(key);
    setGamePhase('loading');
    setInitError(null);
    
    try {
      const response = await gameAPI.initGame(key);
      
      if (response.success) {
        setGameId(response.game_id);
        setActualImpostor(response.impostor_color);
        setGamePhase('playing');
        // Reset game state
        setQuestionsLeft(30);
        setChatHistories({
          red: [],
          yellow: [],
          green: [],
          blue: [],
        });
      } else {
        setInitError(response.message || 'Failed to initialize game');
        setGamePhase('api-key');
      }
    } catch (err) {
      console.error('Failed to initialize game:', err);
      setInitError(err.response?.data?.detail || err.message || 'Failed to connect to server');
      setGamePhase('api-key');
    }
  };

  const handleChatSelect = (color) => {
    setActiveChat(color);
  };

  const handleQuestionSent = () => {
    setQuestionsLeft(prev => {
      const newQuestionsLeft = Math.max(0, prev - 1);
      
      // If questions reach 0, show impostor selection
      if (newQuestionsLeft === 0) {
        setGamePhase('selecting');
      }
      
      return newQuestionsLeft;
    });
  };

  const handleMessageSent = (color, userMessage, assistantResponse) => {
    setChatHistories(prev => ({
      ...prev,
      [color]: [
        ...prev[color],
        { role: 'user', content: userMessage, timestamp: new Date().toISOString() },
        { role: 'assistant', content: assistantResponse, timestamp: new Date().toISOString() },
      ],
    }));
  };

  const handleSelectImpostor = () => {
    setGamePhase('selecting');
  };

  const handleImpostorSelection = async (selectedColor) => {
    try {
      const result = await gameAPI.verifyGuess(gameId, selectedColor);
      
      setGameResult({
        type: result.correct ? 'win' : 'lose',
        message: result.message,
        selectedColor,
        actualImpostor: result.actual_impostor,
      });
      setGamePhase('result');
    } catch (err) {
      console.error('Failed to verify guess:', err);
      // Fallback to local check
      const isCorrect = selectedColor === actualImpostor;
      setGameResult({
        type: isCorrect ? 'win' : 'lose',
        message: isCorrect 
          ? `You found the impostor!`
          : `Wrong! The impostor was ${actualImpostor.toUpperCase()}.`,
        selectedColor,
        actualImpostor,
      });
      setGamePhase('result');
    }
  };

  const handleBackFromSelection = () => {
    setGamePhase('playing');
  };

  const handlePlayAgain = async () => {
    // Clean up old game
    if (gameId) {
      try {
        await gameAPI.deleteGame(gameId);
      } catch (err) {
        console.log('Could not delete old game:', err);
      }
    }
    
    // Start new game with same API key
    if (apiKey) {
      handleApiKeySubmit(apiKey);
    } else {
      setGamePhase('api-key');
      setGameResult(null);
      setGameId(null);
    }
  };

  const handleNewApiKey = () => {
    setGamePhase('api-key');
    setApiKey('');
    setGameResult(null);
    setGameId(null);
  };

  // Render API key input screen
  if (gamePhase === 'api-key' || gamePhase === 'loading') {
    return (
      <div className="app-container">
        <ApiKeyInput 
          onSubmit={handleApiKeySubmit}
          loading={gamePhase === 'loading'}
          error={initError}
        />
      </div>
    );
  }

  // Render impostor selection screen
  if (gamePhase === 'selecting') {
    return (
      <div className="app-container">
        <ImpostorSelection 
          onSelect={handleImpostorSelection}
          actualImpostor={actualImpostor}
          onBack={handleBackFromSelection}
        />
      </div>
    );
  }

  // Render game result screen
  if (gamePhase === 'result' && gameResult) {
    return (
      <div className="app-container">
        <div className={`game-result ${gameResult.type}`}>
          <h2>{gameResult.type === 'win' ? '🎉 VICTORY! 🎉' : '❌ DEFEAT ❌'}</h2>
          <p>{gameResult.message}</p>
          <div className="result-buttons">
            <button className="new-game-button" onClick={handlePlayAgain}>
              Play Again
            </button>
            <button className="new-api-key-button" onClick={handleNewApiKey}>
              Change API Key
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render main game
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Impostor.AI</h1>
      </header>

      <div className="game-content">
        <div className="game-info">
          <Scenario />
          <Stats 
            questionsLeft={questionsLeft}
            onSelectImpostor={handleSelectImpostor}
          />
        </div>
        <div className="game-chat">
          <div className="chat-header">
            <ChatSelector 
              activeChat={activeChat} 
              onChatSelect={handleChatSelect} 
            />
          </div>
          <Chat 
            gameId={gameId}
            color={activeChat}
            messages={chatHistories[activeChat]}
            onQuestionSent={handleQuestionSent}
            onMessageSent={handleMessageSent}
          />
        </div>
      </div>
    </div>
  );
}

export default App;