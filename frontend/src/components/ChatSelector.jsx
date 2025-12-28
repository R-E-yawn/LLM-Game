import redIcon from '../assets/red_icon.png';
import yellowIcon from '../assets/yellow_icon.png';
import greenIcon from '../assets/green_icon.png';
import blueIcon from '../assets/blue_icon.png';

const chatIcons = {
  red: redIcon,
  yellow: yellowIcon,
  green: greenIcon,
  blue: blueIcon,
};

function ChatSelector({ activeChat, onChatSelect }) {
  const colors = ['red', 'yellow', 'blue', 'green'];

  return (
    <div className="chat-selector">
      {colors.map((color) => (
        <div
          key={color}
          className={`chat-square ${activeChat === color ? 'active' : ''}`}
          onClick={() => onChatSelect(color)}
        >
          <img 
            src={chatIcons[color]} 
            alt={`${color} chat`}
            className="chat-icon"
          />
        </div>
      ))}
    </div>
  );
}

export default ChatSelector;

