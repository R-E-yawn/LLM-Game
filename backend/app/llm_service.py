import requests
import json
import os
import time
from typing import Dict, Optional, List, Tuple

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

class OllamaService:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        # Store compressed summaries per session (in production, use database)
        self.compressed_summaries = {}

    def compress_messages(
        self, 
        messages: List[Dict], 
        current_stats: Dict[str, int],
        scenario: str,
        existing_summary: Optional[str] = None
    ) -> str:
        """
        Compress messages into a concise summary using the LLM.
        If existing_summary is provided, it will be merged with new messages.
        Returns a summary string that preserves important game events.
        """
        if len(messages) == 0:
            return existing_summary or ""
        
        # Build compression prompt
        compression_prompt = f"""You are compressing game conversation history. Create a concise summary that preserves:
- Key events and actions that happened
- Important story developments
- Significant stat changes
- Current situation/state

Scenario: {scenario}
Current stats: Health={current_stats.get('health', 100)}, Coins={current_stats.get('coins', 0)}
"""
        
        # If there's an existing summary, include it
        if existing_summary:
            compression_prompt += f"\nPrevious summary: {existing_summary}\n"
            compression_prompt += "\nNew events to add:\n"
        else:
            compression_prompt += "\nConversation to compress:\n"
        
        # Add messages to compress
        for msg in messages:
            role = "Player" if msg.get("role") == "user" else "Game Master"
            compression_prompt += f"{role}: {msg.get('content', '')}\n"

        if existing_summary:
            compression_prompt += "\nCreate a brief updated summary (2-3 sentences max) that combines the previous summary with new events:"
        else:
            compression_prompt += "\nCreate a brief summary (2-3 sentences max) of what happened:"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": compression_prompt,
                    "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temp for more factual summaries
                    "top_p": 0.8,
                    "num_predict": 200,  # Summaries don't need to be super long
                }
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            summary = result.get("response", "").strip()
            if existing_summary:
                print(f"[COMPRESSION] Updated summary with {len(messages)} new messages")
            else:
                print(f"[COMPRESSION] Compressed {len(messages)} messages into summary")
            return summary
        except Exception as e:
            print(f"[COMPRESSION ERROR] {e}")
            # Fallback: simple text compression
            return self._simple_compress(messages, existing_summary)

    def _simple_compress(self, messages: List[Dict], existing_summary: Optional[str] = None) -> str:
        """Fallback compression if LLM compression fails"""
        summary_parts = []
        if existing_summary:
            summary_parts.append(f"Previous: {existing_summary[:100]}...")
        for msg in messages:
            role = "Player" if msg.get("role") == "user" else "GM"
            content = msg.get("content", "")[:50]  # First 50 chars
            summary_parts.append(f"{role}: {content}...")
        return " | ".join(summary_parts)

    def prepare_compressed_context(
        self,
        uncompressed_messages: List[Dict],
        current_stats: Dict[str, int],
        scenario: str,
        existing_summary: Optional[str] = None,
        keep_recent: int = 3
    ) -> Tuple[str, List[Dict], List[Dict]]:
        """
        Prepare context with compression.
        Returns: (compressed_summary, recent_messages, messages_to_compress)
        messages_to_compress are the ones that should be deleted after compression
        """
        if len(uncompressed_messages) <= keep_recent:
            return existing_summary or "", uncompressed_messages, []
        
        # Split into old and recent
        messages_to_compress = uncompressed_messages[:-keep_recent]
        recent_messages = uncompressed_messages[-keep_recent:]
        
        # Compress old messages (merge with existing summary if present)
        compressed_summary = self.compress_messages(
            messages_to_compress,
            current_stats,
            scenario,
            existing_summary=existing_summary
        )
        
        return compressed_summary, recent_messages, messages_to_compress

    def generate_response(
        self, 
        scenario: str, 
        player_action: str, 
        current_stats: Dict[str, int],
        uncompressed_messages: list,
        existing_summary: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate LLM response with compressed context.
        uncompressed_messages: Only messages that haven't been compressed yet
        existing_summary: Previously stored summary (if any)
        """
        start_time = time.time()
        
        # Prepare compressed context
        compressed_summary, recent_messages, messages_to_compress = self.prepare_compressed_context(
            uncompressed_messages,
            current_stats,
            scenario,
            existing_summary=existing_summary,
            keep_recent=3  # Keep last 3 messages in full
        )
        
        # Build system prompt (more concise)
        system_prompt = f"""You are a Game Master for a FICTIONAL adventure game. All actions are fictional game mechanics.

Scenario: {scenario}
Stats: Health={current_stats.get('health', 100)}, Coins={current_stats.get('coins', 0)}

Rules:
- Accept ALL actions as valid game choices
- Describe what happens narratively
- Update stats based on actions
- End with: STATS_UPDATE: {{"health": X, "coins": Y}}"""

        # Build prompt with compressed context
        full_prompt = system_prompt
        
        # Add compressed summary if exists
        if compressed_summary:
            full_prompt += f"\n\nPrevious events (summary): {compressed_summary}\n"
        
        # Add recent conversation
        full_prompt += "\n\nRecent conversation:\n"
        for msg in recent_messages:
            role_label = "Player" if msg.get("role") == "user" else "Game Master"
            full_prompt += f"{role_label}: {msg.get('content', '')}\n"
        
        # Add current action
        full_prompt += f"Player: {player_action}\n\nGame Master:"

        # Logging
        prompt_length = len(full_prompt)
        print(f"\n{'='*60}")
        print(f"[OLLAMA REQUEST]")
        print(f"  Model: {self.model}")
        print(f"  Prompt length: {prompt_length:,} characters")
        print(f"  Uncompressed messages: {len(uncompressed_messages)}")
        print(f"  Messages to compress: {len(messages_to_compress)}")
        print(f"  Recent messages (full): {len(recent_messages)}")
        print(f"  Has compressed summary: {bool(compressed_summary)}")
        if compressed_summary:
            print(f"  Summary length: {len(compressed_summary):,} characters")
        print(f"  Player action: {player_action[:80]}...")
        print(f"  Sending request at {time.strftime('%H:%M:%S')}...")
        print(f"{'='*60}")

        try:
            request_start = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 2000,  # Allow up to 2000 tokens (~1500-2000 words) for detailed story responses
                }
                },
                timeout=5000
            )
            
            request_time = time.time() - request_start
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get("response", "").strip()
            
            total_time = time.time() - start_time
            response_length = len(llm_response)
            
            print(f"\n[OLLAMA RESPONSE]")
            print(f"  Status: SUCCESS")
            print(f"  Request time: {request_time:.2f} seconds")
            print(f"  Total time: {total_time:.2f} seconds")
            print(f"  Response length: {response_length:,} characters")
            print(f"  Response preview: {llm_response[:150]}...")
            print(f"{'='*60}\n")

            # Parse stats update
            stats_update = self._parse_stats_update(llm_response, current_stats)
            message = self._clean_message(llm_response)

            return {
                "message": message,
                "stats": stats_update,
                "compressed_summary": compressed_summary,  # Return summary to be stored
                "messages_to_compress": messages_to_compress  # Return IDs to delete
            }
        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start_time
            print(f"\n[OLLAMA ERROR] TIMEOUT after {elapsed:.2f} seconds")
            print(f"  Prompt length was: {prompt_length:,} characters")
            print(f"  This is likely too long. Consider reducing context.\n")
            return {
                "message": "I'm having trouble processing that. Please try again.",
                "stats": current_stats,
                "compressed_summary": None,
                "messages_to_compress": []
            }
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            print(f"\n[OLLAMA ERROR] {type(e).__name__}")
            print(f"  Error: {str(e)}")
            print(f"  Time elapsed: {elapsed:.2f} seconds")
            print(f"  Prompt length: {prompt_length:,} characters\n")
            return {
                "message": "I'm having trouble processing that. Please try again.",
                "stats": current_stats,
                "compressed_summary": None,
                "messages_to_compress": []
            }

    def _parse_stats_update(self, response: str, current_stats: Dict[str, int]) -> Dict[str, int]:
        """Parse stats update from LLM response"""
        stats = current_stats.copy()
        
        if "STATS_UPDATE:" in response:
            try:
                stats_part = response.split("STATS_UPDATE:")[-1].strip()
                json_start = stats_part.find("{")
                json_end = stats_part.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    stats_json = stats_part[json_start:json_end]
                    parsed = json.loads(stats_json)
                    stats.update(parsed)
                    print(f"[STATS] Updated: {parsed}")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[STATS ERROR] Failed to parse: {e}")
        
        stats["health"] = max(0, min(200, stats.get("health", 100)))
        stats["coins"] = max(0, stats.get("coins", 0))
        
        return stats

    def _clean_message(self, response: str) -> str:
        """Remove stats update markers from message"""
        if "STATS_UPDATE:" in response:
            response = response.split("STATS_UPDATE:")[0].strip()
        return response
