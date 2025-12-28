import { useState, useEffect, useRef } from 'react';
import Message from './Message';
import { gameAPI } from '../services/api';

function Chat({ gameId, color, messages, onQuestionSent, onMessageSent }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [localMessages, setLocalMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Combine parent messages with local typing state
  const displayMessages = [...messages, ...localMessages];

  useEffect(() => {
    scrollToBottom();
  }, [displayMessages]);

  // Reset local messages when switching chats
  useEffect(() => {
    setLocalMessages([]);
  }, [color]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || !gameId) return;

    const userMessage = input.trim();
    
    // Add user message locally for immediate feedback
    setLocalMessages([{ role: 'user', content: userMessage, timestamp: new Date().toISOString() }]);
    setInput('');
    setLoading(true);

    try {
      const response = await gameAPI.chatWithPlayer(gameId, color, userMessage);
      
      if (response.response) {
        // Clear local messages and notify parent
        setLocalMessages([]);
        onMessageSent(color, userMessage, response.response);
        
        // Decrement questions after successful send
        if (onQuestionSent) {
          onQuestionSent();
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message locally
      setLocalMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
          timestamp: new Date().toISOString(),
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getPlayerName = () => {
    const names = {
      red: 'Red',
      yellow: 'Yellow',
      blue: 'Blue',
      green: 'Green',
    };
    return names[color] || 'Player';
  };

  return (
    <div className="chat-container">
      <div className="messages-list">
        {displayMessages.length === 0 ? (
          <div className="empty-messages">
            Start your investigation! Ask {getPlayerName()} questions to figure out if they're the impostor.
          </div>
        ) : (
          displayMessages.map((message, index) => (
            <Message 
              key={index} 
              message={message} 
              playerColor={color}
            />
          ))
        )}
        {loading && (
          <div className="message message-assistant">
            <div className="message-content">
              <div className="message-role">{getPlayerName()}</div>
              <div className="message-text typing">Thinking...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Ask ${getPlayerName()} a question...`}
          disabled={loading || !gameId}
        />
        <button
          type="submit"
          className="chat-send-button"
          disabled={loading || !input.trim() || !gameId}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;