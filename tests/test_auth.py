"""X-API-Key authentication for protected /api/v1 endpoints.

`GET /api/v1/auth/verify` is the first endpoint behind the protected router; it lets an
integrator check that their key is accepted. Health probes must stay public.
"""

import pytest
from conftest import TEST_API_KEYS
from httpx import AsyncClient

VERIFY_URL = "/api/v1/auth/verify"
UNAUTHORIZED_BODY = {"error": {"code": "UNAUTHORIZED", "message": "Invalid or missing API key."}}


@pytest.mark.parametrize("api_key", TEST_API_KEYS)
async def test_valid_key_is_accepted(client: AsyncClient, api_key: str):
    response = await client.get(VERIFY_URL, headers={"X-API-Key": api_key})

    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


async def test_missing_key_is_rejected(client: AsyncClient):
    response = await client.get(VERIFY_URL)

    assert response.status_code == 401
    assert response.json() == UNAUTHORIZED_BODY


@pytest.mark.parametrize(
    "bad_key",
    [
        "wrong-key",
        "",
        "   ",
        "test-key-primar",  # prefix of a valid key
        "test-key-primaryX",  # valid key with extra suffix
        "TEST-KEY-PRIMARY",  # keys are case-sensitive
        " test-key-primary ",  # no silent whitespace trimming
    ],
)
async def test_invalid_key_is_rejected(client: AsyncClient, bad_key: str):
    response = await client.get(VERIFY_URL, headers={"X-API-Key": bad_key})

    assert response.status_code == 401
    # Same body for missing and wrong keys, so callers can't probe which case they hit.
    assert response.json() == UNAUTHORIZED_BODY


async def test_key_in_wrong_header_is_rejected(client: AsyncClient):
    response = await client.get(VERIFY_URL, headers={"Authorization": f"Bearer {TEST_API_KEYS[0]}"})

    assert response.status_code == 401


@pytest.mark.parametrize("path", ["/api/v1/health/liveness", "/api/v1/health/readiness"])
async def test_health_probes_stay_public(client: AsyncClient, path: str):
    response = await client.get(path)

    assert response.status_code == 200


async def test_openapi_declares_api_key_scheme(client: AsyncClient):
    """/docs should offer an Authorize button for X-API-Key."""
    schema = (await client.get("/openapi.json")).json()

    schemes = schema["components"]["securitySchemes"].values()
    assert any(
        s["type"] == "apiKey" and s["in"] == "header" and s["name"] == "X-API-Key" for s in schemes
    )
