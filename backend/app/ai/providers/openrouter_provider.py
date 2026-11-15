import httpx

from app.ai.errors import (
    AIInvalidResponseError,
    AIQuotaError,
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)
from app.ai.types import LLMResult
from app.config import settings

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def _retry_after(response: httpx.Response) -> int | None:
    value = response.headers.get("retry-after", "")
    return int(value) if value.isdigit() else None


class OpenRouterProvider:
    async def generate(self, system_prompt: str, user_message: str) -> str:
        result = await self.generate_chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2500,
        )
        return result.text

    async def generate_chat(
        self, messages: list[dict], max_tokens: int = 2500
    ) -> LLMResult:
        if not settings.openrouter_api_key:
            raise AIUnavailableError("OPENROUTER_API_KEY is missing")

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
                response = await client.post(API_URL, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise AITimeoutError("Provider timed out") from exc
        except httpx.RequestError as exc:
            raise AIUnavailableError("Could not reach provider") from exc

        code = response.status_code
        if code >= 400:
            if code == 402:
                raise AIQuotaError("Provider quota or credits exhausted")
            if code == 429:
                raise AIRateLimitError("Provider rate limit", retry_after=_retry_after(response))
            if code in (401, 403):
                raise AIUnavailableError("Provider rejected credentials")
            if code >= 500:
                raise AIUnavailableError(f"Provider error HTTP {code}")
            raise AIInvalidResponseError(f"Provider rejected request HTTP {code}")

        try:
            data = response.json()
        except ValueError as exc:
            raise AIInvalidResponseError("Provider returned non-JSON") from exc

        choices = data.get("choices")
        if not choices:
            raise AIInvalidResponseError("Provider response missing choices")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            if choices[0].get("finish_reason") == "length":
                raise AIInvalidResponseError("Model hit the output token limit")
            raise AIInvalidResponseError("Provider returned no text")

        usage = data.get("usage") or {}
        return LLMResult(
            text=content.strip(),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            model=str(data.get("model") or settings.openrouter_model),
        )