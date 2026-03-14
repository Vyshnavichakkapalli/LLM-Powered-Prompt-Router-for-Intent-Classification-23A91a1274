import os
import json
import asyncio
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv
from app.models import LogEntry
from app.logger import log_interaction

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "llama-3.1-8b-instant")
EXPERT_MODEL = os.getenv("EXPERT_MODEL", "llama-3.1-8b-instant")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# Configure Groq client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Load prompts from config file
PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts.json")
with open(PROMPTS_PATH, "r") as f:
    PROMPTS_CONFIG = json.load(f)

VALID_INTENTS = list(PROMPTS_CONFIG.keys())

async def classify_intent(message: str) -> Dict[str, Any]:
    """Classifies the user's intent using a focused, lightweight Groq call."""
    if not client:
        print("WARNING: GROQ_API_KEY not set. Defaulting to 'unclear'.")
        return {"intent": "unclear", "confidence": 0.0}

    classifier_system_prompt = (
        "Your task is to classify the user's intent. "
        "Based on the user message below, choose ONE of the following labels: "
        "code, data, writing, career, unclear. "
        "Use these rules: "
        "code = programming, debugging, SQL, scripts, software engineering questions. "
        "data = statistics, metrics, analysis, dashboards, pivot tables, dataset interpretation. "
        "writing = feedback/coaching on existing text quality, tone, clarity, grammar, style. "
        "career = resume, cover letter, interviews, job search, professional growth and career planning. "
        "unclear = vague greetings, mixed intents, or out-of-scope creative generation requests like poems/stories. "
        "Respond with ONLY a single JSON object containing two keys: "
        "'intent' (the label you chose) and 'confidence' (a float from 0.0 to 1.0, representing your certainty). "
        "Do not provide any other text, explanation, or markdown. Example: {\"intent\": \"code\", \"confidence\": 0.95}"
    )

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=CLASSIFIER_MODEL,
            messages=[
                {"role": "system", "content": classifier_system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = (response.choices[0].message.content or "").strip()

        # Strip any accidental markdown fences
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        data = json.loads(content)

        # Validate schema
        if "intent" not in data or "confidence" not in data:
            raise ValueError("Malformed JSON: missing 'intent' or 'confidence' keys")

        # Sanitize values
        if data["intent"] not in VALID_INTENTS:
            data["intent"] = "unclear"

        data["confidence"] = float(data["confidence"])
        return data

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Classification JSON parse error: {e}")
        return {"intent": "unclear", "confidence": 0.0}
    except Exception as e:
        print(f"Classification API error: {e}")
        return {"intent": "unclear", "confidence": 0.0}


async def route_and_respond(message: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Routes the request to the appropriate expert persona and generates a response."""
    intent = intent_data.get("intent", "unclear")
    confidence = float(intent_data.get("confidence", 0.0))

    if not client:
        fallback_response = "Could you clarify if you need help with coding, data analysis, writing, or career advice?"
        log_interaction(LogEntry(
            intent="unclear",
            confidence=0.0,
            user_message=message,
            final_response=fallback_response
        ))
        return {
            "intent": "unclear",
            "confidence": 0.0,
            "response": fallback_response,
        }

    # Apply confidence threshold — low-confidence responses go to clarifier
    if confidence < CONFIDENCE_THRESHOLD:
        intent = "unclear"

    expert_config = PROMPTS_CONFIG.get(intent, PROMPTS_CONFIG["unclear"])
    system_prompt = expert_config["system_prompt"]

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=EXPERT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
        )
        final_response = (response.choices[0].message.content or "").strip()
        if not final_response:
            final_response = "Could you share a bit more detail so I can help effectively?"

        # Log the interaction
        log_entry = LogEntry(
            intent=intent,
            confidence=confidence,
            user_message=message,
            final_response=final_response
        )
        log_interaction(log_entry)

        return {
            "intent": intent,
            "confidence": confidence,
            "response": final_response,
        }

    except Exception as e:
        error_msg = f"Sorry, I encountered an error generating a response: {str(e)}"
        # Still log the error for observability
        log_interaction(LogEntry(
            intent=intent,
            confidence=confidence,
            user_message=message,
            final_response=error_msg
        ))
        return {
            "intent": intent,
            "confidence": confidence,
            "response": error_msg,
        }
