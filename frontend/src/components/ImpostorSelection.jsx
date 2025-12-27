import redIcon from '../assets/red_icon.png';
import yellowIcon from '../assets/yellow_icon.png';
import greenIcon from '../assets/green_icon.png';
import blueIcon from '../assets/blue_icon.png';

const impostorIcons = {
  red: redIcon,
  yellow: yellowIcon,
  green: greenIcon,
  blue: blueIcon,
};

function ImpostorSelection({ onSelect, actualImpostor, onBack }) {
  const colors = ['red', 'yellow', 'green', 'blue'];
  
  const handleSelect = (color) => {
    const isCorrect = color === actualImpostor;
    onSelect(color, isCorrect);
  };
  
  return (
    <div className="impostor-selection-screen">
      <button className="back-button" onClick={onBack}>
        ← Back
      </button>
      <h2>Who is the Impostor?</h2>
      <div className="impostor-options">
        {colors.map(color => (
          <button 
            key={color}
            className={`impostor-option impostor-option-${color}`}
            onClick={() => handleSelect(color)}
          >
            <img 
              src={impostorIcons[color]} 
              alt={`${color} crewmate`}
              className="impostor-option-icon"
            />
            <span className="impostor-option-label">{color.toUpperCase()}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default ImpostorSelection;

