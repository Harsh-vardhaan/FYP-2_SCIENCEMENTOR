"""Local Ollama provider implementation."""
import os
from typing import Optional, List, Dict

import requests

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider for running open-source LLMs."""

    def __init__(self) -> None:
        """Initialize the Ollama provider."""
        self._base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = "llama3.2"  # Default model, can be changed

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "ollama"

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def generate_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using local Ollama."""
        prompt = self.build_prompt(question, context)
        
        # Build messages for Ollama chat format
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000,
                    },
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e
