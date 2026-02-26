"""Google Gemini provider implementation."""
import os
from typing import Optional, List, Dict

from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self) -> None:
        """Initialize the Gemini provider."""
        self._api_key = os.getenv("GOOGLE_API_KEY", "")
        self._model = None
        if self._api_key and self._api_key != "your_gemini_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    system_instruction=self.SYSTEM_PROMPT,
                )
            except ImportError:
                pass

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "gemini"

    def is_available(self) -> bool:
        """Check if Gemini is configured."""
        return self._model is not None

    def generate_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using Gemini."""
        if not self._model:
            raise RuntimeError("Gemini model not initialized")

        prompt = self.build_prompt(question, context)
        
        # Build conversation history for Gemini format
        history = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})

        # Start chat with history
        chat = self._model.start_chat(history=history)

        response = chat.send_message(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1000,
            },
        )

        return response.text if response.text else ""
