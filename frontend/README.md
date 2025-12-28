# Impostor.AI - Among Us-style Deduction Game

An interactive deduction game where you chat with AI-powered crewmates to find the impostor. One of the four AI players is secretly the impostor - can you figure out who?

## Features

- **AI-Powered Players**: Chat with 4 distinct AI crewmates (Red, Yellow, Blue, Green)
- **Dynamic Event Generation**: Each game generates unique events and scenarios
- **Intelligent Impostor**: The impostor uses advanced AI to deceive and deflect
- **Truthful Crewmates**: Non-impostors answer honestly based on their observations
- **Limited Questions**: You have 30 questions to figure out who's lying
- **GPT-4.1 Powered**: Uses OpenAI's latest model for intelligent responses

## How It Works

1. **Event Generation**: When you start a game, the system generates 10 time periods of events using AI
2. **Impostor Assignment**: An AI analyzes the events and assigns one player as the impostor
3. **Role-Based Prompts**: 
   - Crewmates receive instructions to be truthful and helpful
   - The impostor receives instructions to lie, deflect, and avoid detection
4. **Investigation**: Chat with each player, asking questions about what they saw
5. **Final Decision**: When ready (or after 30 questions), make your accusation

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- OpenAI API key with access to GPT-4.1

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start the backend server (see Backend Setup)
2. Start the frontend server (see Frontend Setup)
3. Open your browser to `http://localhost:5173`
4. Enter your OpenAI API key
5. Wait for the game to generate (30-60 seconds)
6. Start chatting with the players to find the impostor!

## Gameplay Tips

- Ask about specific events and timings
- Cross-reference what different players say
- The impostor will try to:
  - Deflect blame onto others
  - Provide vague or inconsistent answers
  - Claim alibis they might not have
- Crewmates will:
  - Be consistent with their observations
  - Provide specific details about what they saw
  - Admit when they don't know something

## Project Structure

```
Impostor.AI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application and routes
│   │   ├── database.py          # Database setup
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── game_state.py        # Game state management
│   │   ├── llm_service.py       # OpenAI GPT-4.1 integration
│   │   └── event_generator.py   # Event generation and impostor assignment
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ApiKeyInput.jsx  # API key entry screen
│   │   │   ├── Chat.jsx         # Chat interface
│   │   │   ├── ChatSelector.jsx # Player selector
│   │   │   ├── ImpostorSelection.jsx
│   │   │   ├── Message.jsx      # Chat message component
│   │   │   ├── Scenario.jsx
│   │   │   └── Stats.jsx
│   │   ├── services/
│   │   │   └── api.js          # API client
│   │   ├── utils/
│   │   │   └── formatMessage.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   └── package.json
└── README.md
```

## API Endpoints

- `POST /api/game/init` - Initialize a new game with API key
- `POST /api/game/chat` - Send a message to a player
- `GET /api/game/{game_id}/state` - Get current game state
- `GET /api/game/{game_id}/history/{color}` - Get chat history for a player
- `POST /api/game/{game_id}/verify?guess={color}` - Verify impostor guess
- `DELETE /api/game/{game_id}` - Delete a game session

## Privacy Note

Your OpenAI API key is only stored in memory during your game session and is never persisted to disk. Each game session is independent and cleaned up when you start a new game.

## Troubleshooting

- **"Invalid API key" error**: Make sure your OpenAI API key is valid and has access to GPT-4.1
- **Game generation takes too long**: The initial generation makes ~12 API calls, which can take 30-60 seconds
- **Backend won't start**: Make sure the virtual environment is activated and all dependencies are installed
- **CORS errors**: Ensure the frontend URL is in the CORS allowed origins in `backend/app/main.py`

## License

This project is open source and available for personal and educational use.