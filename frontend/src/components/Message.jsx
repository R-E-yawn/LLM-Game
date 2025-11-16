import { formatMessage } from '../utils/formatMessage';

function Message({ message }) {
  const isUser = message.role === 'user';
  
  // Format assistant messages (convert markdown to HTML)
  // Keep user messages plain text
  const displayContent = isUser 
    ? message.content 
    : formatMessage(message.content);
  
  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className="message-content">
        <div className="message-role">{isUser ? 'You' : 'Game Master'}</div>
        {isUser ? (
          <div className="message-text">{message.content}</div>
        ) : (
          <div 
            className="message-text" 
            dangerouslySetInnerHTML={{ __html: displayContent }}
          />
        )}
        {message.timestamp && (
          <div className="message-time">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;

