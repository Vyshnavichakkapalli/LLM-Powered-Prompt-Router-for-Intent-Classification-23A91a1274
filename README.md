# LLM-Powered Prompt Router for Intent Classification

This project implements an intent-based AI router using Python and Groq. It classifies a user's message into one of several supported intents, selects a specialized expert persona prompt, generates a response, and logs the full interaction to a JSON Lines file.

Supported intents:
- `code`
- `data`
- `writing`
- `career`
- `unclear`

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Input                               │
│              (CLI · FastAPI UI · curl · /chat)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Manual Override?      │  @code / @data /
              │   (prefix detection)    │  @writing / @career
              └────────┬────────────────┘
               YES ◄───┘         │ NO
                │                ▼
                │   ┌────────────────────────────┐
                │   │     classify_intent()       │
                │   │  ─────────────────────────  │
                │   │  Groq LLM call              │
                │   │  model : llama-3.1-8b-inst  │
                │   │  temp  : 0.0                │
                │   │  mode  : json_object        │
                │   │  ─────────────────────────  │
                │   │  Returns:                   │
                │   │  { "intent":     "code",    │
                │   │    "confidence":  0.92 }    │
                │   └────────────┬───────────────┘
                │                │
                │                ▼
                │   ┌────────────────────────────┐
                │   │   Confidence Threshold      │
                │   │   < 0.7  →  force "unclear"│
                │   └────────────┬───────────────┘
                │                │
                └───────►        ▼
                    ┌────────────────────────────────────────────┐
                    │           route_and_respond()              │
                    │   Looks up intent in app/prompts.json      │
                    │                                            │
                    │  "code"    → 🧑‍💻 Code Expert               │
                    │  "data"    → 📊 Data Analyst               │
                    │  "writing" → ✍️  Writing Coach             │
                    │  "career"  → 💼 Career Advisor             │
                    │  "unclear" → 🤔 Ask Clarifying Question    │
                    │                                            │
                    │  Second Groq call with expert system prompt│
                    │  model : llama-3.1-8b-instant              │
                    │  temp  : 0.2                               │
                    └────────────────┬───────────────────────────┘
                                     │
                    ┌────────────────▼───────────────────────────┐
                    │            log_interaction()               │
                    │  Appends to route_log.jsonl                │
                    │  { intent, confidence,                     │
                    │    user_message, final_response,           │
                    │    timestamp }                             │
                    └────────────────┬───────────────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────────────────┐
                    │          Final Response to User            │
                    └────────────────────────────────────────────┘
```

## How It Works

The system uses a two-step pipeline:

1. `classify_intent(message)` makes a lightweight Groq call and returns structured JSON:

```json
{
  "intent": "code",
  "confidence": 0.92
}
```

2. `route_and_respond(message, intent_data)` selects the matching expert persona and makes a second Groq call to generate the final response.

If the intent is `unclear`, or if the confidence falls below the configured threshold (default `0.7`), the system asks a clarifying question instead of guessing.

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── prompts.json
│   ├── router.py
│   └── templates/
│       └── index.html
├── classifier.py
├── cli.py
├── Dockerfile
├── docker-compose.yml
├── llm_client.py
├── logger_util.py
├── prompts.py
├── requirements.txt
├── router.py
├── test_router.py
└── verify_requirements.py
```

## Requirements

- Python 3.11+
- A Groq API key
- Optional: Docker Desktop

## Environment Setup

Create a local `.env` file based on `.env.example`:

```env
GROQ_API_KEY=your_groq_api_key_here
CLASSIFIER_MODEL=llama-3.1-8b-instant
EXPERT_MODEL=llama-3.1-8b-instant
CONFIDENCE_THRESHOLD=0.7
LOG_FILE=route_log.jsonl
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Locally

### FastAPI web app

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

### Interactive CLI

```bash
python cli.py
```

### Batch test suite

```bash
python test_router.py
```

## Run with Docker

### Start the app

```bash
docker compose up --build -d
```

Open:
- `http://localhost:8000`
- `http://localhost:8000/docs`

### Stop the app

```bash
docker compose down
```

### Run the batch test in Docker

```bash
docker compose run --rm --profile test test
```

## Example API Requests

### Chat request

```bash
curl.exe -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"what is machine language\"}"
```

### Health check

```bash
curl.exe http://127.0.0.1:8000/health
```

## Logging

Each request is appended to `route_log.jsonl` as a single JSON object. Each log entry includes:

- `intent`
- `confidence`
- `user_message`
- `final_response`
- `timestamp`

Useful PowerShell commands:

```powershell
Get-Content route_log.jsonl | Select-Object -Last 10
(Get-Content route_log.jsonl).Count
Get-Content route_log.jsonl | Select-Object -Last 1 | ConvertFrom-Json | Format-List
```

## Manual Override

You can bypass classification by prefixing the input with one of these markers:

- `@code`
- `@data`
- `@writing`
- `@career`

Example:

```text
@code fix this python loop
```

## Verification

To verify the implementation against the assignment requirements:

```bash
python verify_requirements.py
```

This checks:
- expert persona prompt coverage
- classifier output schema
- routing behavior
- unclear-intent clarification behavior
- JSONL logging
- malformed JSON fallback handling

## Notes

- `.env` is intentionally ignored by git and should never be committed.
- `app/prompts.json` stores the expert personas in a configurable format.
- The root-level modules support CLI and testing, while the `app/` package supports the FastAPI web interface.