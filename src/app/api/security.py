from fastapi import Request, Security
from fastapi.security import APIKeyHeader

from app.services.auth import ApiKeyAuthenticator

API_KEY_HEADER = "X-API-Key"

# auto_error=False so a missing header reaches the authenticator and gets the standard
# {"error": {...}} 401 body instead of FastAPI's default 403.
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


async def require_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
) -> None:
    """Router dependency: rejects the request with 401 unless X-API-Key is valid."""
    authenticator = await request.state.dishka_container.get(ApiKeyAuthenticator)
    authenticator.authenticate(api_key)
