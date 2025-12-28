"""
Event Generator Module
Generates game events through iterative LLM calls and assigns impostor
"""

import json
from typing import Dict, List, Optional
from openai import OpenAI

# Player color mapping
PLAYER_COLORS = {
    "Player1": "red",
    "Player2": "yellow", 
    "Player3": "blue",
    "Player4": "green"
}

COLOR_TO_PLAYER = {v: k for k, v in PLAYER_COLORS.items()}

EVENT_GENERATION_PROMPT = """You are generating events for an Among Us-style game. 
There are 4 players: Player1, Player2, Player3, and Player4.
The game takes place on a spaceship with these locations: Cafeteria, Admin, Storage, Electrical, 
Lower Engine, Upper Engine, Security, Reactor, MedBay, O2, Weapons, Shields, Communications, Navigation.

Rules:
- No two players can be in the exact same location at the same timestamp unless explicitly described as meeting
- Players should move between adjacent locations realistically
- Include tasks being completed, players crossing paths, meetings, etc.
- Make events interesting and varied
- Each time period should have 2-4 events

Generate events for time period {time_index}. 

Previous events (for context and continuity):
{previous_events}

Output ONLY valid JSON in this exact format with no additional text:
{{
  "time": {time_index},
  "events": [
    {{
      "event_id": <unique_number>,
      "description": "<detailed description of what happened>",
      "players": ["<player names involved>"]
    }}
  ]
}}
"""

IMPOSTOR_ASSIGNMENT_PROMPT = """Based on the following event history from an Among Us game, select ONE player to be the Impostor.
Consider which player had opportunities to be alone, was in isolated areas, or could have committed a kill.

Event History:
{event_history}

You must select exactly one impostor from: Player1, Player2, Player3, Player4.

Also, create a brief "murder event" that happened during the game - describe when and where the impostor 
killed a victim (you can make the victim a 5th NPC crew member who was found dead).

Output ONLY valid JSON in this exact format:
{{
  "impostor": "<Player name>",
  "murder_event": {{
    "time": <time_period when murder occurred>,
    "location": "<where it happened>",
    "victim": "Crewmate5",
    "description": "<brief description of the murder>",
    "witnesses": ["<any players who might have seen something suspicious>"]
  }}
}}
"""


class EventGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.1"
    
    def generate_single_time_period(self, time_index: int, previous_events: List[Dict]) -> Dict:
        """Generate events for a single time period"""
        previous_events_str = json.dumps(previous_events, indent=2) if previous_events else "None (this is the first time period)"
        
        prompt = EVENT_GENERATION_PROMPT.format(
            time_index=time_index,
            previous_events=previous_events_str
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a game event generator. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            # Clean up potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
        except Exception as e:
            print(f"[EVENT_GENERATOR] Error generating events for time {time_index}: {e}")
            # Return a fallback event
            return {
                "time": time_index,
                "events": [
                    {
                        "event_id": time_index * 10 + 1,
                        "description": f"Players continue their tasks around the ship at time {time_index}.",
                        "players": ["Player1", "Player2", "Player3", "Player4"]
                    }
                ]
            }
    
    def generate_all_events(self, num_periods: int = 10) -> List[Dict]:
        """Generate events for all time periods iteratively"""
        all_events = []
        
        for time_index in range(num_periods):
            print(f"[EVENT_GENERATOR] Generating events for time period {time_index}...")
            time_period_events = self.generate_single_time_period(time_index, all_events)
            all_events.append(time_period_events)
        
        return all_events
    
    def assign_impostor(self, all_events: List[Dict]) -> Dict:
        """Use LLM to assign the impostor based on event history"""
        event_history_str = json.dumps(all_events, indent=2)
        
        prompt = IMPOSTOR_ASSIGNMENT_PROMPT.format(event_history=event_history_str)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are assigning the impostor role. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            # Clean up potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
        except Exception as e:
            print(f"[EVENT_GENERATOR] Error assigning impostor: {e}")
            # Fallback to Player1
            return {
                "impostor": "Player1",
                "murder_event": {
                    "time": 5,
                    "location": "Electrical",
                    "victim": "Crewmate5",
                    "description": "Player1 eliminated Crewmate5 in Electrical while no one was watching.",
                    "witnesses": []
                }
            }
    
    def get_player_events(self, all_events: List[Dict], player_name: str) -> List[Dict]:
        """Extract events that a specific player was involved in"""
        player_events = []
        
        for time_period in all_events:
            time = time_period.get("time", 0)
            for event in time_period.get("events", []):
                if player_name in event.get("players", []):
                    player_events.append({
                        "time": time,
                        "event_id": event.get("event_id"),
                        "description": event.get("description"),
                        "players": event.get("players")
                    })
        
        return player_events
    
    def build_player_event_data(self, all_events: List[Dict]) -> Dict[str, List[Dict]]:
        """Build event data for all players"""
        player_data = {}
        
        for player_name in PLAYER_COLORS.keys():
            player_data[player_name] = self.get_player_events(all_events, player_name)
        
        return player_data


def generate_game_data(api_key: str, num_periods: int = 10) -> Dict:
    """
    Main function to generate complete game data
    Returns: {
        "all_events": [...],
        "player_events": {"Player1": [...], ...},
        "impostor_data": {"impostor": "...", "murder_event": {...}},
        "impostor_color": "red/yellow/blue/green"
    }
    """
    generator = EventGenerator(api_key)
    
    # Generate all events
    print("[GAME_DATA] Generating event history...")
    all_events = generator.generate_all_events(num_periods)
    
    # Build per-player event data
    print("[GAME_DATA] Building player event data...")
    player_events = generator.build_player_event_data(all_events)
    
    # Assign impostor
    print("[GAME_DATA] Assigning impostor...")
    impostor_data = generator.assign_impostor(all_events)
    
    impostor_player = impostor_data.get("impostor", "Player1")
    impostor_color = PLAYER_COLORS.get(impostor_player, "red")
    
    return {
        "all_events": all_events,
        "player_events": player_events,
        "impostor_data": impostor_data,
        "impostor_color": impostor_color
    }