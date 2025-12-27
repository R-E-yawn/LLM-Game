function Stats({ questionsLeft, onSelectImpostor }) {
  return (
    <div className="stats-container">
      <h2>Questions Left</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">Questions:</span>
          <span className="stat-value">{questionsLeft || 30}</span>
        </div>
      </div>
      <button 
        className="select-impostor-button"
        onClick={onSelectImpostor}
      >
        Select Impostor
      </button>
    </div>
  );
}

export default Stats;

