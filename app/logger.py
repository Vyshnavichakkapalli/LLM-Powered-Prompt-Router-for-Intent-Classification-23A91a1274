import json
from app.models import LogEntry

# Configure logging to a file
LOG_FILE = "route_log.jsonl"

def log_interaction(entry: LogEntry):
    """Logs the interaction to a JSON Lines file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.dict()) + "\n")
    except Exception as e:
        print(f"Error logging interaction: {e}")
