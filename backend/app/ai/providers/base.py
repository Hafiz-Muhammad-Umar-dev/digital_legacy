from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        """Generate a response from an AI model."""
        raise NotImplementedError