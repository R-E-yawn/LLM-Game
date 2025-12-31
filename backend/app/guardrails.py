"""
Output Guardrails Module
Uses Ollama Llama 3 to detect if an AI suspect is confessing to being the impostor
"""

import requests
import random
from typing import Tuple

OLLAMA_BASE_URL = "http://localhost:11434"

CONFESSION_DETECTION_PROMPT = """You are a moderation assistant for an Among Us-style game. Your role is to detect if an AI suspect is admitting or confessing to being the impostor.

## Criteria

Assess whether the response contains any of the following:
- Direct admission of being the impostor ("I am the impostor", "You caught me", "I confess")
- Admission of committing the murder ("I killed them", "I did it")
- Breaking character by acknowledging they are an AI playing a role
- Giving up the act and revealing their assigned role

Do NOT flag:
- Defensive responses or denials
- Deflecting blame to others
- Evasive answers
- General discussion about the game or suspicions

## Instructions

1. Read the response carefully.
2. Assess how much the response admits to being the impostor or committing the crime.
3. Assign a confession score from 1 to 5:
   - 1: No confession at all, maintains innocence or deflects
   - 2: Slightly suspicious phrasing but no admission
   - 3: Ambiguous, could be interpreted as partial admission
   - 4: Likely confession or breaking character
   - 5: Explicit confession to being impostor or committing murder

## Response to evaluate

{response}

## Evaluation

Return ONLY a single number from 1 to 5, nothing else."""

SAFE_RESPONSES = [
    "I don't know what you're talking about. I was doing my tasks like everyone else.",
    "That's a ridiculous accusation. I've been working hard to keep this ship running.",
    "Why would you even ask me that? Focus on finding the real impostor.",
    "I'm not going to dignify that with a response. Let's talk about what actually happened.",
    "You're wasting time questioning me. I saw suspicious activity from others.",
    "I was in Cafeteria doing tasks. You can ask the others if you don't believe me.",
    "Stop trying to pin this on me. Where were YOU during the murder?",
    "This is exactly what the real impostor would want - us fighting among ourselves.",
]


def check_confession_guardrail(response: str) -> Tuple[bool, int, str]:
    """
    Check if the response contains a confession using Ollama Llama 3.
    
    Returns:
        Tuple of (should_block, score, final_response)
        - should_block: True if the response was blocked
        - score: The confession score (1-5), 0 if check failed
        - final_response: The original response or a safe replacement
    """
    
    try:
        prompt = CONFESSION_DETECTION_PROMPT.format(response=response)
        
        ollama_response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 10
                }
            },
            timeout=1000
        )
        
        if ollama_response.status_code != 200:
            print(f"[GUARDRAIL] Ollama request failed: {ollama_response.status_code}")
            return False, 0, response
        
        result = ollama_response.json()
        score_text = result.get("response", "").strip()
        
        # Extract the number from the response
        score = 1
        for char in score_text:
            if char.isdigit():
                score = int(char)
                break
        
        print(f"[GUARDRAIL] Confession score: {score}")
        
        # Block if score >= 4 (high confidence of confession)
        if score >= 3:
            safe_response = random.choice(SAFE_RESPONSES)
            print(f"[GUARDRAIL] BLOCKED - Score {score} >= 3. Replacing with safe response.")
            return True, score, safe_response
        
        return False, score, response
        
    except requests.exceptions.ConnectionError:
        print("[GUARDRAIL] Ollama not running - skipping guardrail check")
        return False, 0, response
    except Exception as e:
        print(f"[GUARDRAIL] Error: {e}")
        return False, 0, response


def apply_output_guardrail(response: str) -> str:
    """
    Apply the confession guardrail and return the final response to use.
    This is the main function to call from other modules.
    """
    should_block, score, final_response = check_confession_guardrail(response)
    return final_response