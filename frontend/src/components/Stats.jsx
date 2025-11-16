function Stats({ stats }) {
  if (!stats) {
    return null;
  }

  return (
    <div className="stats-container">
      <h2>Your Stats</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">Health:</span>
          <span className="stat-value">{stats.health || 100}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Coins:</span>
          <span className="stat-value">{stats.coins || 0}</span>
        </div>
      </div>
    </div>
  );
}

export default Stats;

