from app.config import settings

class OllamaProvider:
    def __init__(self):
        self.client = ollama.AsyncClient(
            host=settings.ollama_base_url,
            headers={
                "Authorization": f"Bearer {settings.ollama_api_key}"
            },
        )
        self.model = settings.ollama_model

    async def generate(self, system_prompt: str, user_message: str) -> str:
        response = await self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.message.content or ""