import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const gameAPI = {
  startGame: async (scenario) => {
    const response = await api.post('/game/start', { scenario });
    return response.data;
  },

  sendAction: async (sessionId, action) => {
    const response = await api.post(`/game/${sessionId}/action`, { action });
    return response.data;
  },

  getState: async (sessionId) => {
    const response = await api.get(`/game/${sessionId}/state`);
    return response.data;
  },

  getMessages: async (sessionId) => {
    const response = await api.get(`/game/${sessionId}/messages`);
    return response.data;
  },
};

export default api;

