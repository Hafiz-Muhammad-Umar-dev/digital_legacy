class AIProviderError(Exception):
    def __init__(self, message: str, *, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class AITimeoutError(AIProviderError):
    pass


class AIRateLimitError(AIProviderError):
    pass


class AIQuotaError(AIProviderError):
    pass


class AIInvalidResponseError(AIProviderError):
    pass


class AIUnavailableError(AIProviderError):
    pass