"""
router.py  (root-level, synchronous)
Implements route_and_respond() — selects the right expert persona and calls
the LLM for the final, high-quality response.
"""
import os
from prompts import PROMPTS_CONFIG
from llm_client import client

# Confidence threshold: below this value the request is treated as 'unclear'
_CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
_EXPERT_MODEL = os.getenv("EXPERT_MODEL", "llama-3.1-8b-instant")


def route_and_respond(message: str, intent_data: dict) -> str:
    """
    Uses the classified intent to select the appropriate expert system prompt
    and makes a second LLM call to generate the final response.

    Args:
        message:     The original user message.
        intent_data: Dict with keys 'intent' (str) and 'confidence' (float),
                     as returned by classify_intent().

    Returns:
        The final response string from the expert persona.
        If intent is 'unclear', returns a clarifying question instead.
    """
    intent = intent_data.get("intent", "unclear")
    confidence = float(intent_data.get("confidence", 0.0))

    # Apply confidence threshold (Stretch Goal)
    if confidence < _CONFIDENCE_THRESHOLD:
        intent = "unclear"

    # Requirement 4: 'unclear' → ask for clarification, never guess
    expert_config = PROMPTS_CONFIG.get(intent, PROMPTS_CONFIG["unclear"])
    system_prompt = expert_config["system_prompt"]

    try:
        response = client.call(
            system_prompt,
            message,
            model=_EXPERT_MODEL,
            temperature=0.2,
        )
        return response or "Could you share a bit more detail so I can help effectively?"
    except Exception as e:
        print(f"[router] Expert LLM call failed: {e}")
        return (
            "I encountered an error generating a response. "
            "Could you clarify whether you need help with coding, data analysis, "
            "writing, or career advice?"
        )
