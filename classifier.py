# classifier.py
import json
from prompts import CLASSIFIER_PROMPT, PROMPTS_CONFIG
from llm_client import client

# Valid intent labels drawn directly from the loaded prompts config
_VALID_INTENTS = set(PROMPTS_CONFIG.keys())

# Manual override prefixes: '@code Fix this bug' → intent='code', confidence=1.0
_MANUAL_OVERRIDES: dict[str, str] = {
    "@code": "code",
    "@data": "data",
    "@writing": "writing",
    "@career": "career",
}


def classify_intent(message: str) -> dict:
    """
    Takes a user message and classifies its intent via a lightweight LLM call.

    Supports manual overrides via '@' prefix (e.g. '@code fix this').
    Returns a dict: {'intent': str, 'confidence': float}.
    Defaults to {'intent': 'unclear', 'confidence': 0.0} on any error.
    """
    # --- Stretch Goal: Manual override detection ---
    lower = message.lower()
    for prefix, intent_label in _MANUAL_OVERRIDES.items():
        if lower.startswith(prefix):
            return {"intent": intent_label, "confidence": 1.0}

    try:
        # json_mode=True forces the model to emit valid JSON only
        response_text = client.call(
            CLASSIFIER_PROMPT,
            message,
            json_mode=True,
            temperature=0.0,
        )

        # Strip accidental markdown fences (extra safety)
        if response_text.startswith("```"):
            parts = response_text.split("```")
            response_text = parts[1].lstrip("json").strip() if len(parts) > 1 else ""

        data = json.loads(response_text)

        # Validate required keys exist
        if "intent" not in data or "confidence" not in data:
            raise ValueError("Missing 'intent' or 'confidence' keys in LLM response")

        # Sanitize: unknown labels become 'unclear'
        intent = str(data["intent"])
        if intent not in _VALID_INTENTS:
            intent = "unclear"

        return {
            "intent": intent,
            "confidence": float(data["confidence"]),
        }

    except (json.JSONDecodeError, ValueError) as e:
        # Requirement 6: gracefully handle malformed JSON
        print(f"[classifier] JSON parse error: {e}")
        return {"intent": "unclear", "confidence": 0.0}
    except Exception as e:
        print(f"[classifier] API error: {e}")
        return {"intent": "unclear", "confidence": 0.0}
