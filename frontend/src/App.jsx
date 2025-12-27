import { useState, useEffect } from 'react';
import Scenario from './components/Scenario';
import Stats from './components/Stats';
import Chat from './components/Chat';
import ChatSelector from './components/ChatSelector';
import ImpostorSelection from './components/ImpostorSelection';
import { gameAPI } from './services/api';
import './App.css';

function App() {
  const [chats, setChats] = useState({
    red: { sessionId: null, scenario: '', initialized: false },
    yellow: { sessionId: null, scenario: '', initialized: false },
    green: { sessionId: null, scenario: '', initialized: false },
    blue: { sessionId: null, scenario: '', initialized: false },
  });
  const [activeChat, setActiveChat] = useState('yellow');
  const [questionsLeft, setQuestionsLeft] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showImpostorSelection, setShowImpostorSelection] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [actualImpostor, setActualImpostor] = useState(() => {
    // Randomly select the impostor at game start
    const colors = ['red', 'yellow', 'green', 'blue'];
    return colors[Math.floor(Math.random() * colors.length)];
  });

  const defaultScenario = 
    "You're playing Among Us. One of these 4 is the impostor. Chat with them and ask questions to figure out who the impostor is.";

  // Initialize all chats on mount
  useEffect(() => {
    const initializeAllChats = async () => {
      setLoading(true);
      setError(null);

      try {
        const newChats = {};
        const colors = ['red', 'yellow', 'green', 'blue'];
        
        for (const color of colors) {
          const response = await gameAPI.startGame(defaultScenario);
          newChats[color] = {
            sessionId: response.session_id,
            scenario: defaultScenario,
            initialized: true,
          };
        }
        
        setChats(newChats);
        setActiveChat('yellow'); // Start with yellow
      } catch (err) {
        console.error('Failed to initialize chats:', err);
        setError('Failed to initialize chats. Make sure the backend server is running.');
      } finally {
        setLoading(false);
      }
    };

    initializeAllChats();
  }, []);

  const handleChatSelect = (color) => {
    if (chats[color].initialized) {
      setActiveChat(color);
    }
  };

  const handleQuestionSent = () => {
    setQuestionsLeft(prev => {
      const newQuestionsLeft = Math.max(0, prev - 1);
      
      // If questions reach 0, show impostor selection
      if (newQuestionsLeft === 0) {
        setShowImpostorSelection(true);
      }
      
      return newQuestionsLeft;
    });
  };

  const handleSelectImpostor = () => {
    setShowImpostorSelection(true);
  };

  const handleImpostorSelection = (selectedColor, isCorrect) => {
    setShowImpostorSelection(false);
    
    if (isCorrect) {
      setGameResult({
        type: 'win',
        message: `You eliminated the impostor! You were right! The impostor was ${selectedColor.toUpperCase()}.`,
      });
    } else {
      setGameResult({
        type: 'lose',
        message: `You kicked out a crewmate! The impostor was ${actualImpostor.toUpperCase()}. You lost.`,
      });
    }
  };

  const handleCloseResult = () => {
    setGameResult(null);
    setQuestionsLeft(30);
    // Randomly select new impostor
    const colors = ['red', 'yellow', 'green', 'blue'];
    setActualImpostor(colors[Math.floor(Math.random() * colors.length)]);
    
    // Reset all chats
    const newChats = {};
    
    const resetChats = async () => {
      setLoading(true);
      try {
        for (const color of colors) {
          const response = await gameAPI.startGame(defaultScenario);
          newChats[color] = {
            sessionId: response.session_id,
            scenario: defaultScenario,
            initialized: true,
          };
        }
        setChats(newChats);
        setActiveChat('yellow');
      } catch (err) {
        console.error('Failed to reset chats:', err);
      } finally {
        setLoading(false);
      }
    };
    
    resetChats();
  };

  const handleBackFromSelection = () => {
    setShowImpostorSelection(false);
  };

  const activeChatData = activeChat ? chats[activeChat] : null;

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Starting game...</div>
      </div>
    );
  }

  if (showImpostorSelection) {
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

  if (gameResult) {
    return (
      <div className="app-container">
        <div className={`game-result ${gameResult.type}`}>
          <h2>{gameResult.type === 'win' ? '🎉 VICTORY! 🎉' : '❌ DEFEAT ❌'}</h2>
          <p>{gameResult.message}</p>
          <button className="new-game-button" onClick={handleCloseResult}>
            Play Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Impostor.AI</h1>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

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
            sessionId={activeChatData?.sessionId} 
            onQuestionSent={handleQuestionSent}
            color={activeChat}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
