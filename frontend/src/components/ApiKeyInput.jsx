import { useState } from 'react';

function ApiKeyInput({ onSubmit, loading, error }) {
  const [apiKey, setApiKey] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (apiKey.trim()) {
      onSubmit(apiKey.trim());
    }
  };

  return (
    <div className="api-key-screen">
      <div className="api-key-container">
        <h1 className="api-key-title">🚀 Impostor.AI</h1>
        <p className="api-key-subtitle">An Among Us-style deduction game powered by AI</p>
        
        <form onSubmit={handleSubmit} className="api-key-form">
          <div className="api-key-input-wrapper">
            <label htmlFor="api-key" className="api-key-label">
              Enter your OpenAI API Key
            </label>
            <input
              id="api-key"
              type="password"
              className="api-key-input"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              disabled={loading}
              autoComplete="off"
            />
            <p className="api-key-hint">
              Your API key is used to power the AI players. It's only stored locally during your session.
            </p>
          </div>
          
          {error && (
            <div className="api-key-error">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            className="api-key-submit"
            disabled={!apiKey.trim() || loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Generating Game...
              </>
            ) : (
              'Start Game'
            )}
          </button>
        </form>
        
        {loading && (
          <div className="generation-status">
            <p>🎲 Generating event history...</p>
            <p>🔍 Assigning impostor...</p>
            <p>🎭 Preparing AI players...</p>
            <p className="generation-note">This may take 30-60 seconds</p>
          </div>
        )}
        
        <div className="api-key-info">
          <h3>How to play:</h3>
          <ul>
            <li>Chat with 4 AI crewmates (Red, Yellow, Blue, Green)</li>
            <li>One of them is secretly the Impostor</li>
            <li>Ask questions to figure out who's lying</li>
            <li>You have 30 questions to find the Impostor</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ApiKeyInput;