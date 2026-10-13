class SoccerAError(Exception):
    """Base class for all application-raised errors."""


class DataSourceError(SoccerAError):
    """Raised when a data source adapter fails to fetch or parse data."""


class RateLimitExceededError(DataSourceError):
    """Raised when a provider's rate limit is hit and retries are exhausted."""


class DataSourceAuthError(DataSourceError):
    """Raised on 401/403 responses — invalid or missing API credentials."""
