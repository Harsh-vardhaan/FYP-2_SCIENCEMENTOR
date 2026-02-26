"""Factory for creating LLM provider instances."""
import os
from typing import Dict, List, Optional

from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider


class LLMProviderFactory:
    """Factory for managing and creating LLM providers."""

    _providers: Dict[str, BaseLLMProvider] = {}
    _initialized: bool = False

    @classmethod
    def _initialize(cls) -> None:
        """Initialize all providers."""
        if cls._initialized:
            return
        cls._providers = {
            "openai": OpenAIProvider(),
            "claude": ClaudeProvider(),
            "gemini": GeminiProvider(),
            "ollama": OllamaProvider(),
        }
        cls._initialized = True

    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> BaseLLMProvider:
        """Get a provider by name or return the default.
        
        Args:
            name: Provider name (openai, claude, gemini, ollama).
                  If None, uses DEFAULT_LLM_PROVIDER from environment.
                  
        Returns:
            The requested LLM provider.
            
        Raises:
            ValueError: If the provider is not found or not available.
        """
        cls._initialize()

        if name is None:
            name = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

        name = name.lower()
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")

        provider = cls._providers[name]
        if not provider.is_available():
            raise ValueError(f"Provider '{name}' is not configured or available")

        return provider

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get a list of all available (configured) providers.
        
        Returns:
            List of provider names that are ready to use.
        """
        cls._initialize()
        return [
            name for name, provider in cls._providers.items()
            if provider.is_available()
        ]

    @classmethod
    def get_all_providers(cls) -> List[str]:
        """Get a list of all provider names.
        
        Returns:
            List of all provider names.
        """
        cls._initialize()
        return list(cls._providers.keys())
