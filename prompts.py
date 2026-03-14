"""
prompts.py
Loads expert persona prompts from app/prompts.json and exposes:
  - PROMPTS_CONFIG  : dict keyed by intent label
  - CLASSIFIER_PROMPT : the system prompt used by classify_intent()
"""
import json
import os

# ---------------------------------------------------------------------------
# Load expert persona prompts from the shared config file
# ---------------------------------------------------------------------------
_PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "app", "prompts.json")
with open(_PROMPTS_PATH, "r", encoding="utf-8") as _f:
    PROMPTS_CONFIG: dict = json.load(_f)

# ---------------------------------------------------------------------------
# Classifier system prompt
# Engineered to be short, focused, and to return ONLY valid JSON.
# ---------------------------------------------------------------------------
CLASSIFIER_PROMPT: str = (
    "Your task is to classify the user's intent. "
    "Based on the user message below, choose exactly ONE of the following labels: "
    "code, data, writing, career, unclear. "
    "Use these definitions:\n"
    "  code    — programming, debugging, SQL, scripts, software engineering questions.\n"
    "  data    — statistics, metrics, analysis, pivot tables, dashboards, dataset interpretation.\n"
    "  writing — feedback or coaching on existing text: tone, clarity, grammar, style.\n"
    "  career  — resume, cover letter, interviews, job search, or professional growth planning.\n"
    "  unclear — vague greetings, mixed/ambiguous intents, or out-of-scope creative requests "
    "(e.g. poems, stories).\n"
    "Respond with ONLY a single JSON object containing exactly two keys:\n"
    "  'intent'     — the label you chose (string)\n"
    "  'confidence' — your certainty as a float from 0.0 to 1.0\n"
    "Do not include any other text, explanation, or markdown fences.\n"
    "Example: {\"intent\": \"code\", \"confidence\": 0.95}"
)
