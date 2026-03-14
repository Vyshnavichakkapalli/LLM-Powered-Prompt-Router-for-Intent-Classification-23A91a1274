"""
test_router.py
Runs 15+ test messages through the full classify → route → respond pipeline.
Results are printed to the console and logged to route_log.jsonl.

Usage:  python test_router.py
"""
import textwrap
from classifier import classify_intent
from router import route_and_respond
from logger_util import log_interaction

# ---------------------------------------------------------------------------
# 15 required test messages (plus a few edge-case extras)
# ---------------------------------------------------------------------------
TEST_MESSAGES = [
    # Clear single-intent messages
    "how do i sort a list of objects in python?",                         # → code
    "explain this sql query for me",                                      # → code
    "This paragraph sounds awkward, can you help me fix it?",             # → writing
    "I'm preparing for a job interview, any tips?",                       # → career
    "what's the average of these numbers: 12, 45, 23, 67, 34",           # → data
    # Ambiguous / edge-case messages
    "Help me make this better.",                                          # → unclear (vague)
    (
        "I need to write a function that takes a user id and returns "
        "their profile, but also i need help with my resume."
    ),                                                                    # → mixed (unclear)
    "hey",                                                                # → unclear
    "Can you write me a poem about clouds?",                              # → unclear
    "Rewrite this sentence to be more professional.",                     # → writing
    "I'm not sure what to do with my career.",                            # → career
    "what is a pivot table",                                              # → data
    "fxi thsi bug pls: for i in range(10) print(i)",                      # → code (typos)
    "How do I structure a cover letter?",                                 # → career
    "My boss says my writing is too verbose.",                            # → writing
    # Stretch-goal: manual overrides
    "@code def fib(n): pass  # implement fibonacci",                     # → code (override)
    "@data I have sales figures for Q1 through Q4, what should I check?",# → data (override)
    # Extra edge cases
    "Can you analyse the distribution of customer churn rates?",          # → data
    "How does binary search work?",                                       # → code
    "What should I put in a LinkedIn summary?",                           # → career
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
SEPARATOR = "─" * 65


def run_tests():
    print("=" * 65)
    print("   LLM Prompt Router — Batch Test Suite")
    print("=" * 65)
    print(f"Running {len(TEST_MESSAGES)} test messages...\n")

    for idx, message in enumerate(TEST_MESSAGES, start=1):
        print(f"\n[{idx:02d}] MESSAGE: {message[:80]}{'...' if len(message) > 80 else ''}")
        print(SEPARATOR)

        # Step 1 — Classify
        intent_data = classify_intent(message)
        intent     = intent_data["intent"]
        confidence = intent_data["confidence"]
        print(f"     Intent    : {intent}")
        print(f"     Confidence: {confidence:.2f}")

        # Step 2 — Route & Respond
        response = route_and_respond(message, intent_data)

        # Pretty-print the response (wrapped at 70 chars)
        wrapped = textwrap.fill(response, width=70, initial_indent="     ",
                                subsequent_indent="     ")
        print(f"\n     Response:\n{wrapped}")
        print(SEPARATOR)

        # Step 3 — Log
        log_interaction(intent, confidence, message, response)

    print("\n✓ All tests complete. Log written to route_log.jsonl")


if __name__ == "__main__":
    run_tests()
