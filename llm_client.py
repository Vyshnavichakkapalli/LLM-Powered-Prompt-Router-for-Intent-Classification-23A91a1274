"""
llm_client.py
Thin synchronous wrapper around the Groq API client.
Exports a single `client` object used by classifier.py and router.py.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Synchronous Groq client wrapper with a simple call() interface."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self._groq = Groq(api_key=api_key) if api_key else None
        self.classifier_model = os.getenv("CLASSIFIER_MODEL", "llama-3.1-8b-instant")
        self.expert_model = os.getenv("EXPERT_MODEL", "llama-3.1-8b-instant")

    def call(
        self,
        system_prompt: str,
        user_message: str,
        *,
        model: str = None,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> str:
        """
        Makes a chat completion call to Groq.

        Args:
            system_prompt: The system instruction for the LLM.
            user_message:  The user's input text.
            model:         Override the default model.
            temperature:   Sampling temperature (0 = deterministic).
            json_mode:     If True, instructs the model to return valid JSON only.

        Returns:
            The raw text content from the LLM response, or an empty string on failure.
        """
        if not self._groq:
            print("[llm_client] WARNING: GROQ_API_KEY not set — returning empty string.")
            return ""

        kwargs: dict = {
            "model": model or self.classifier_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._groq.chat.completions.create(**kwargs)
        return (response.choices[0].message.content or "").strip()


# Module-level singleton — import this everywhere
client = LLMClient()
