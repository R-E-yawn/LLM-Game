function Scenario() {
  const scenarioText = "You're playing Among Us. One of these 4 is the impostor. Chat with them and ask questions to figure out who the impostor is.";

  return (
    <div className="scenario-container">
      <h2>Scenario</h2>
      <div className="scenario-content">{scenarioText}</div>
    </div>
  );
}

export default Scenario;

