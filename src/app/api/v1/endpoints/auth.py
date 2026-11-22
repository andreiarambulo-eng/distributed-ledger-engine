from fastapi import APIRouter

from app.api.schemas import AuthVerifyResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/verify",
    response_model=AuthVerifyResponse,
    summary="Verify API Key",
    description="Returns 200 if the X-API-Key header holds a valid key, otherwise 401.",
)
async def verify_api_key() -> AuthVerifyResponse:
    # Reaching this handler means require_api_key on the protected router already passed.
    return AuthVerifyResponse(authenticated=True)
