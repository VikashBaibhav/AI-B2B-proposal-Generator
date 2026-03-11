"""
Domain Interface — AI Service (Abstract)

Defines the contract that any AI provider must fulfill.
The application layer depends ONLY on this abstraction — never on OpenAI directly.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIRequest:
    """Standard request object passed to any AI service implementation."""
    system_prompt: str
    user_prompt: str
    temperature: float = 0.7
    max_tokens: int = 4096
    response_format: str = "json_object"  # or "text"
    model: Optional[str] = None           # Override default model if needed


@dataclass
class AIResponse:
    """Standard response object returned by any AI service implementation."""
    content: str                 # Raw string content from the model
    model: str                   # Actual model used
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str           # "stop" | "length" | "content_filter"
    raw_response: Optional[dict] = None  # Full raw provider response for debugging


class AIService(ABC):
    """
    Abstract base class for AI text generation services.

    Implement this interface for any provider (OpenAI, Anthropic, Gemini, etc.)
    to keep the application layer fully decoupled from specific SDKs.
    """

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Send a prompt to the AI model and return a structured response.

        Args:
            request: An AIRequest containing system/user prompts and parameters.

        Returns:
            An AIResponse with the generated content and metadata.

        Raises:
            AIServiceError: On API failures, rate limits, or timeout.
        """
        ...

    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model name used by this service implementation."""
        ...


class AIServiceError(Exception):
    """Raised when the AI service encounters an unrecoverable error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
