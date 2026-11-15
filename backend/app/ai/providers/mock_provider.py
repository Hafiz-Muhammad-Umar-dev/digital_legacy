from app.ai.providers.base import LLMProvider


class MockProvider(LLMProvider):
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        return (
            "Yeh backend ka test response hai. "
            "Abhi real LLM connect nahi hai. "
            f"Tumhara message receive hua: {user_message}"
        )