function Scenario({ scenario }) {
  if (!scenario) {
    return null;
  }

  return (
    <div className="scenario-container">
      <h2>Scenario</h2>
      <div className="scenario-content">{scenario}</div>
    </div>
  );
}

export default Scenario;

