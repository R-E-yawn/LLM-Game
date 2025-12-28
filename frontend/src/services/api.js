import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const gameAPI = {
  // Initialize a new game with API key
  initGame: async (apiKey) => {
    const response = await api.post('/game/init', { api_key: apiKey });
    return response.data;
  },

  // Send a message to a specific player
  chatWithPlayer: async (gameId, color, message) => {
    const response = await api.post('/game/chat', {
      game_id: gameId,
      color: color,
      message: message,
    });
    return response.data;
  },

  // Get game state
  getGameState: async (gameId) => {
    const response = await api.get(`/game/${gameId}/state`);
    return response.data;
  },

  // Get chat history for a player
  getChatHistory: async (gameId, color) => {
    const response = await api.get(`/game/${gameId}/history/${color}`);
    return response.data;
  },

  // Get player's events (for debugging)
  getPlayerEvents: async (gameId, color) => {
    const response = await api.get(`/game/${gameId}/events/${color}`);
    return response.data;
  },

  // Verify impostor guess
  verifyGuess: async (gameId, guess) => {
    const response = await api.post(`/game/${gameId}/verify?guess=${guess}`);
    return response.data;
  },

  // Delete/cleanup game
  deleteGame: async (gameId) => {
    const response = await api.delete(`/game/${gameId}`);
    return response.data;
  },

  // Legacy methods for backwards compatibility
  startGame: async (scenario) => {
    console.warn('startGame is deprecated, use initGame instead');
    return { session_id: 'legacy', scenario };
  },

  sendAction: async (sessionId, action) => {
    console.warn('sendAction is deprecated, use chatWithPlayer instead');
    return { message: 'Use chatWithPlayer instead' };
  },

  getState: async (sessionId) => {
    console.warn('getState is deprecated, use getGameState instead');
    return {};
  },

  getMessages: async (sessionId) => {
    console.warn('getMessages is deprecated, use getChatHistory instead');
    return { messages: [] };
  },
};

export default api;