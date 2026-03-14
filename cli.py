# cli.py - Interactive Prompt Router CLI
from classifier import classify_intent
from router import route_and_respond
from logger_util import log_interaction

def main():
    print("=" * 55)
    print("   🤖 LLM-Powered Prompt Router — Interactive Mode")
    print("=" * 55)
    print("Type your message and press Enter to route it.")
    print("Tips:")
    print("  • Use @code, @data, @writing, @career to override")
    print("  • Type 'quit' or 'exit' to stop")
    print("-" * 55)

    while True:
        try:
            user_input = input("\n>>> YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        # Classify
        intent_data = classify_intent(user_input)
        intent     = intent_data["intent"]
        confidence = intent_data["confidence"]

        print(f"--- Intent   : [{intent}]")
        print(f"--- Confidence: {confidence}")

        # Route & Respond
        response = route_and_respond(user_input, intent_data)
        print(f"\n💬 RESPONSE:\n{response}")
        print("-" * 55)

        # Log
        log_interaction(intent, confidence, user_input, response)

if __name__ == "__main__":
    main()
