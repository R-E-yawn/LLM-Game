import { useState, useEffect, useRef } from 'react';
import Message from './Message';
import { gameAPI } from '../services/api';

function Chat({ sessionId, onStateUpdate }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (sessionId) {
      loadMessages();
    }
  }, [sessionId]);

  const loadMessages = async () => {
    try {
      const data = await gameAPI.getMessages(sessionId);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || !sessionId) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await gameAPI.sendAction(sessionId, input.trim());
      
      if (response.message) {
        const assistantMessage = {
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }

      if (response.stats) {
        onStateUpdate(response.stats);
      }

      // Refresh state to get latest stats
      const state = await gameAPI.getState(sessionId);
      if (state.stats) {
        onStateUpdate(state.stats);
      }
    } catch (error) {
      console.error('Failed to send action:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-list">
        {messages.length === 0 ? (
          <div className="empty-messages">
            Start your adventure! Type an action to begin.
          </div>
        ) : (
          messages.map((message, index) => (
            <Message key={index} message={message} />
          ))
        )}
        {loading && (
          <div className="message message-assistant">
            <div className="message-content">
              <div className="message-role">Game Master</div>
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
          placeholder="What do you want to do?"
          disabled={loading || !sessionId}
        />
        <button
          type="submit"
          className="chat-send-button"
          disabled={loading || !input.trim() || !sessionId}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;

