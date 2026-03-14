"""
logger_util.py
Appends every routing decision and final response to route_log.jsonl.
Each line is a self-contained JSON object (JSON Lines format).
"""
import json
import os
from datetime import datetime, timezone

LOG_FILE = os.getenv("LOG_FILE", "route_log.jsonl")


def log_interaction(
    intent: str,
    confidence: float,
    user_message: str,
    final_response: str,
) -> None:
    """
    Appends a single routing event to the JSON Lines log file.

    Each log entry contains at minimum:
      intent, confidence, user_message, final_response, timestamp
    """
    entry = {
        "intent": intent,
        "confidence": confidence,
        "user_message": user_message,
        "final_response": final_response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[logger] Error writing to {LOG_FILE}: {e}")
