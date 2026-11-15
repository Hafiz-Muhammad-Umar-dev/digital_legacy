from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.openrouter_provider import OpenRouterProvider
from app.config import settings


def get_llm_provider():
    if settings.ai_provider == "openrouter":
        return OpenRouterProvider()
    if settings.ai_provider == "ollama":
        return OllamaProvider()
    return MockProvider()


def get_model_name():
    if settings.ai_provider == "openrouter":
        return settings.openrouter_model
    if settings.ai_provider == "ollama":
        return settings.ollama_model
    return "mock"