"""OpenAI GPT provider implementation."""
import os
from typing import Optional, List, Dict

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-3.5/4 provider."""

    def __init__(self) -> None:
        """Initialize the OpenAI provider."""
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self._client = None
        if self._api_key and self._api_key != "sk_your_key_here":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                pass

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "openai"

    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return self._client is not None

    def generate_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using OpenAI GPT."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        prompt = self.build_prompt(question, context)

        # Build messages with conversation history
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content or ""
