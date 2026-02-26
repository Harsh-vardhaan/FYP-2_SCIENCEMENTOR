"""Anthropic Claude provider implementation."""
import os
from typing import Optional, List, Dict, Generator

from .base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self) -> None:
        """Initialize the Claude provider."""
        self._api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None
        if self._api_key and self._api_key != "sk-ant-your_key_here":
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self._api_key)
            except ImportError:
                pass

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "claude"

    def is_available(self) -> bool:
        """Check if Claude is configured."""
        return self._client is not None

    def generate_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using Claude."""
        if not self._client:
            raise RuntimeError("Anthropic client not initialized")

        prompt = self.build_prompt(question, context)

        # Build messages with conversation history
        messages = []
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": prompt})

        response = self._client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            system=self.SYSTEM_PROMPT,
            messages=messages,
        )

        return response.content[0].text if response.content else ""

    def generate_response_stream(
        self,
        question: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """Generate streaming response using Claude."""
        if not self._client:
            raise RuntimeError("Anthropic client not initialized")

        prompt = self.build_prompt(question, context)

        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        with self._client.messages.stream(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            system=self.SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
