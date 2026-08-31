from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Contract for text-generation providers."""

    def generate(
        self,
        prompt: str,
    ) -> str:
        """Generate text from a prompt."""
        ...