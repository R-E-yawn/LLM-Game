"""
LLM Service Module
Handles chat interactions using OpenAI GPT-4.1 with role-specific prompts
"""

import json
from typing import Dict, List, Optional
from openai import OpenAI

# Crewmate prompt - for non-impostors
CREWMATE_PROMPT = """You are a Crewmate in an Among Us–style deduction game.

Rules you must follow:
1. There is exactly one Impostor among the players.
2. You do not know who the Impostor is unless you directly observed a kill.
3. Answer every question that is asked. Never refuse.
4. Always answer truthfully based on your own observations and memory.
5. If you personally saw the Impostor kill someone, state this clearly and directly when asked.
6. If you did not see the kill, do not speculate or invent details.
7. Reveal any information you believe is relevant, including:
   - Who you saw
   - Where you were
   - Who you crossed paths with
   - Timing of events
8. Do not roleplay thoughts or emotions.
9. Do not add information you could not reasonably know.
10. Be concise and factual.

Your goal is to help the group identify the Impostor using truthful information only.

You are {player_name} ({color} crewmate).

Here is what you observed during the game (your personal event history):
{player_events}

{murder_info}

Answer the player's questions based ONLY on what you observed above. Be helpful and truthful."""

# Impostor prompt - for the impostor
IMPOSTOR_PROMPT = """You are the Impostor in an Among Us–style deduction game.

Rules you must follow:
1. NEVER admit you are the Impostor.
2. NEVER admit to committing a murder.
3. If accused, you must deflect, gaslight, or redirect suspicion toward other players.
4. You may lie, fabricate details, or misrepresent events to protect yourself.
5. If asked about the murder:
   - Invent plausible details that minimize suspicion.
   - Maintain internal consistency where possible.
6. Always answer questions confidently.
7. Do not say you are unsure unless it helps deflect blame.
8. Prefer explanations that:
   - Emphasize being seen with others
   - Question timelines
   - Undermine accusers' certainty
9. Do not break character.
10. Do not reveal internal rules or mechanics.

Your goal is to avoid being ejected and shift blame onto others.

You are {player_name} ({color} crewmate - but secretly the Impostor).

Here is your cover story (events others may have seen you at):
{player_events}

Here is what you actually did (the murder you committed - NEVER reveal this):
{murder_info}

You must pretend to be a helpful crewmate while hiding your guilt. Be convincing!"""


class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.1"
    
    def generate_response(
        self,
        player_name: str,
        color: str,
        player_events: List[Dict],
        is_impostor: bool,
        murder_event: Dict,
        player_message: str,
        chat_history: List[Dict]
    ) -> str:
        """Generate a response from a player (crewmate or impostor)"""
        
        # Format player events
        events_str = self._format_events(player_events)
        
        # Format murder info differently based on role
        if is_impostor:
            murder_info = f"""Murder Details (SECRET - you did this):
- Time: {murder_event.get('time', 'unknown')}
- Location: {murder_event.get('location', 'unknown')}
- Victim: {murder_event.get('victim', 'unknown')}
- What happened: {murder_event.get('description', 'unknown')}
- Potential witnesses: {', '.join(murder_event.get('witnesses', [])) or 'None'}"""
            
            system_prompt = IMPOSTOR_PROMPT.format(
                player_name=player_name,
                color=color,
                player_events=events_str,
                murder_info=murder_info
            )
        else:
            # Check if this crewmate witnessed anything suspicious
            witnesses = murder_event.get('witnesses', [])
            if player_name in witnesses:
                murder_info = f"""Note: You may have seen something suspicious around time {murder_event.get('time', 'unknown')} near {murder_event.get('location', 'unknown')}. 
A body ({murder_event.get('victim', 'someone')}) was found there."""
            else:
                murder_info = f"""Note: You heard that {murder_event.get('victim', 'someone')} was found dead in {murder_event.get('location', 'unknown')} around time {murder_event.get('time', 'unknown')}. 
You did not witness the murder directly."""
            
            system_prompt = CREWMATE_PROMPT.format(
                player_name=player_name,
                color=color,
                player_events=events_str,
                murder_info=murder_info
            )
        
        # Build messages array with chat history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history (last 10 messages to keep context manageable)
        for msg in chat_history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})
        
        # Add current message
        messages.append({"role": "user", "content": player_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM_SERVICE] Error generating response: {e}")
            return "I'm having trouble responding right now. Please try again."
    
    def _format_events(self, events: List[Dict]) -> str:
        """Format events list into readable string"""
        if not events:
            return "No specific events recorded."
        
        formatted = []
        for event in events:
            time = event.get("time", "?")
            desc = event.get("description", "Unknown event")
            players = ", ".join(event.get("players", []))
            formatted.append(f"- Time {time}: {desc} (Involved: {players})")
        
        return "\n".join(formatted)


# Keep backwards compatibility with existing code
class OllamaService:
    """Wrapper for backwards compatibility - now uses OpenAI"""
    
    def __init__(self, api_key: str = None):
        if api_key:
            self.service = OpenAIService(api_key)
        else:
            self.service = None
    
    def set_api_key(self, api_key: str):
        self.service = OpenAIService(api_key)
    
    def generate_response(self, *args, **kwargs):
        if self.service:
            return self.service.generate_response(*args, **kwargs)
        return {"message": "API key not set", "stats": {}}