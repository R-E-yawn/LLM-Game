# Story AI Game

An interactive story game where players chat with an LLM (via Ollama) to navigate through scenarios, with stats tracking (health, coins) and a beautiful chat interface.

## Features

- Interactive chat-based gameplay
- LLM-powered game master (via Ollama)
- Real-time stat tracking (health, coins)
- Persistent game state with SQLite database
- Modern React frontend with Vite
- FastAPI backend with CORS support

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- Ollama installed and running locally
- An Ollama model installed (e.g., `llama3`, `mistral`)

### Installing Ollama

1. Download and install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3
   ```
   or
   ```bash
   ollama pull mistral
   ```

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

4. (Optional) Set environment variables:
   ```bash
   export OLLAMA_BASE_URL=http://localhost:11434
   export OLLAMA_MODEL=llama3
   ```

5. Start the backend server:
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

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Start the backend server (see Backend Setup)

3. Start the frontend server (see Frontend Setup)

4. Open your browser to `http://localhost:5173`

5. The game will automatically start with a default scenario. You can:
   - View your stats (health, coins) at the top
   - Read the scenario description
   - Type actions in the chat to interact with the game
   - Watch as the LLM responds and updates your stats

## Project Structure

```
Story AI Game/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application and routes
│   │   ├── database.py      # Database setup
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── game_state.py    # Game state management
│   │   └── llm_service.py   # Ollama integration
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.jsx
│   │   │   ├── Stats.jsx
│   │   │   ├── Scenario.jsx
│   │   │   └── Message.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
└── README.md
```

## API Endpoints

- `POST /api/game/start` - Start a new game session
- `POST /api/game/{session_id}/action` - Send a player action
- `GET /api/game/{session_id}/state` - Get current game state
- `GET /api/game/{session_id}/messages` - Get chat history

## Customization

### Changing the LLM Model

Edit `backend/app/llm_service.py` or set the `OLLAMA_MODEL` environment variable:
```bash
export OLLAMA_MODEL=mistral
```

### Custom Scenarios

Modify the default scenario in `frontend/src/App.jsx` or send a custom scenario when starting a game.

### Fine-tuning with LoRA

To fine-tune the model with LoRA:

1. Prepare your training data (conversations in the game format)
2. Use a tool like `llama.cpp` or `unsloth` for LoRA fine-tuning
3. Convert the fine-tuned model to Ollama format
4. Update the `OLLAMA_MODEL` environment variable to use your fine-tuned model

## Troubleshooting

- **Backend won't start**: Make sure the virtual environment is activated and all dependencies are installed
- **LLM not responding**: Check that Ollama is running (`ollama serve`) and the model is installed (`ollama list`)
- **CORS errors**: Ensure the frontend URL is in the CORS allowed origins in `backend/app/main.py`
- **Database errors**: Delete `database.db` and restart the backend to recreate the database

## License

This project is open source and available for personal and educational use.

