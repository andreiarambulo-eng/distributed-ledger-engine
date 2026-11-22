import hmac

from app.core.config import Settings
from app.domain.exceptions import AuthenticationError


class ApiKeyAuthenticator:
    """Validates a presented API key against the keys configured in API_KEYS."""

    def __init__(self, settings: Settings) -> None:
        self._keys = tuple(key.get_secret_value().encode() for key in settings.api_keys)

    def authenticate(self, presented_key: str | None) -> None:
        if not presented_key:
            raise AuthenticationError()

        presented = presented_key.encode()
        # Check every key without short-circuiting, so response timing doesn't reveal
        # whether (or which) key matched.
        matched = False
        for key in self._keys:
            matched |= hmac.compare_digest(presented, key)

        if not matched:
            raise AuthenticationError()
