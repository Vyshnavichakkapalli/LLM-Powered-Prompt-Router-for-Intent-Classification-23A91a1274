"""
verify_requirements.py
Verifies all 6 core requirements from the project spec.
Run: python verify_requirements.py
"""
import json
import os
import sys

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

results = []

def check(label, condition, detail=""):
    mark = PASS if condition else FAIL
    print(f"{mark} {label}")
    if detail:
        print(f"       {detail}")
    results.append(condition)

print("=" * 60)
print("   Requirement Verification — LLM Prompt Router")
print("=" * 60)

# ── Requirement 1: At least 4 distinct expert system prompts ──────────────────
print("\n[REQ 1] At least 4 expert system prompts in prompts.json")
try:
    with open("app/prompts.json", encoding="utf-8") as f:
        prompts = json.load(f)
    expert_keys = [k for k in prompts if k != "unclear"]
    check("4+ expert personas defined", len(expert_keys) >= 4,
          f"Found: {expert_keys}")
    for key, val in prompts.items():
        has_prompt = "system_prompt" in val and len(val["system_prompt"]) > 20
        check(f"  Persona '{key}' has a substantive system_prompt", has_prompt)
except Exception as e:
    check("prompts.json loads successfully", False, str(e))

# ── Requirement 2: classify_intent returns correct schema ─────────────────────
print("\n[REQ 2] classify_intent() returns {{intent, confidence}}")
try:
    from classifier import classify_intent
    result = classify_intent("how do I sort a list in python?")
    check("classify_intent is callable", True)
    check("Returns 'intent' key", "intent" in result, f"Got: {result}")
    check("Returns 'confidence' key", "confidence" in result, f"Got: {result}")
    check("confidence is a float", isinstance(result["confidence"], float),
          f"Type: {type(result['confidence'])}")
    check("intent is a string", isinstance(result["intent"], str),
          f"Value: {result['intent']}")
    print(f"       {INFO} Result: {result}")
except Exception as e:
    check("classify_intent importable & callable", False, str(e))

# ── Requirement 3: route_and_respond returns a string ─────────────────────────
print("\n[REQ 3] route_and_respond() returns a response string")
try:
    from router import route_and_respond
    resp = route_and_respond("how do I sort a list?", {"intent": "code", "confidence": 0.95})
    check("route_and_respond is callable", True)
    check("Returns a non-empty string", isinstance(resp, str) and len(resp) > 0,
          f"Length: {len(resp)} chars")
except Exception as e:
    check("route_and_respond importable & callable", False, str(e))

# ── Requirement 4: 'unclear' intent → clarifying question ────────────────────
print("\n[REQ 4] 'unclear' intent generates a clarifying question")
try:
    from router import route_and_respond
    unclear_resp = route_and_respond("hey", {"intent": "unclear", "confidence": 0.9})
    is_question = "?" in unclear_resp
    check("Response to 'unclear' contains a question mark", is_question,
          f"Response snippet: {unclear_resp[:120]}...")
except Exception as e:
    check("'unclear' routing works", False, str(e))

# ── Requirement 5: route_log.jsonl has valid entries with required keys ───────
print("\n[REQ 5] route_log.jsonl logging")
log_path = os.getenv("LOG_FILE", "route_log.jsonl")
if os.path.exists(log_path):
    required_keys = {"intent", "confidence", "user_message", "final_response"}
    valid_lines = 0
    total_lines = 0
    errors = []
    with open(log_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            try:
                entry = json.loads(line)
                missing = required_keys - set(entry.keys())
                if missing:
                    errors.append(f"Line {i} missing keys: {missing}")
                else:
                    valid_lines += 1
            except json.JSONDecodeError as e:
                errors.append(f"Line {i} invalid JSON: {e}")
    check(f"Log file exists ({log_path})", True)
    check(f"All {total_lines} entries are valid JSON", len(errors) == 0,
          "; ".join(errors) if errors else "")
    check("Entries contain all required keys", valid_lines == total_lines,
          f"{valid_lines}/{total_lines} valid")
    print(f"       {INFO} Total log entries: {total_lines}")
else:
    check(f"Log file exists ({log_path})", False,
          "Run test_router.py or cli.py first to generate logs")

# ── Requirement 6: graceful handling of malformed JSON ───────────────────────
print("\n[REQ 6] classify_intent() handles malformed LLM response gracefully")
try:
    from classifier import classify_intent
    from unittest.mock import patch, MagicMock

    mock_client = MagicMock()
    mock_client.call.return_value = "THIS IS NOT JSON AT ALL <<<>>>"

    with patch("classifier.client", mock_client):
        result = classify_intent("test message")

    check("No exception raised on malformed JSON", True)
    check("Defaults to intent='unclear'", result["intent"] == "unclear",
          f"Got: {result['intent']}")
    check("Defaults to confidence=0.0", result["confidence"] == 0.0,
          f"Got: {result['confidence']}")
except Exception as e:
    check("Graceful malformed-JSON handling", False, str(e))

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(results)
total  = len(results)
color  = "\033[92m" if passed == total else "\033[93m"
print(f"{color}Results: {passed}/{total} checks passed\033[0m")
print("=" * 60)

sys.exit(0 if passed == total else 1)
