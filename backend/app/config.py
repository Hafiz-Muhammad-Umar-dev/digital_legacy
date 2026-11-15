from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Digital Legacy API"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Database
    database_url: str = "sqlite:///./digital_legacy.db"

    # AI provider settings
    ai_provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = "liquid/lfm-2.5-2.6b:free"

    # Ollama fallback
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b-instruct"

    # Upload settings
    max_upload_mb: int = 500

    # Authentication / JWT
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
        # AI limits
    ai_timeout_seconds: int = 90
    chat_max_output_tokens: int = 800
    chat_history_turns: int = 10
    chat_history_char_budget: int = 6000
    chat_memory_limit: int = 10
    daily_token_limit_per_user: int = 100000
    # Paid model ho to USD per 1M tokens likho (free model ke liye 0)
    ai_price_input_per_1m: float = 0.0
    ai_price_output_per_1m: float = 0.0


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

if not settings.jwt_secret_key:
    raise RuntimeError("JWT_SECRET_KEY .env mein set karo")
