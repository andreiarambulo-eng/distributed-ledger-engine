"""Real application startup/shutdown.

The `client` fixture uses httpx.ASGITransport, which never runs the lifespan, so it cannot
catch startup failures. These tests drive the ASGI lifespan protocol directly, exactly as
uvicorn does. Nothing here resolves a dependency, so no database or Redis connection opens.
"""

from fastapi import FastAPI

from app.main import create_app

LIFESPAN_OK = ["lifespan.startup.complete", "lifespan.shutdown.complete"]


async def run_lifespan(app: FastAPI) -> list[str]:
    """Send startup then shutdown to the app; return the message types it replied with."""
    incoming = [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]
    replies: list[str] = []

    async def receive() -> dict:
        return incoming.pop(0)

    async def send(message: dict) -> None:
        replies.append(message["type"])

    scope = {"type": "lifespan", "asgi": {"version": "3.0"}, "state": {}}
    await app(scope, receive, send)
    return replies


async def test_app_with_default_container_starts_and_shuts_down():
    assert await run_lifespan(create_app()) == LIFESPAN_OK


async def test_app_can_be_started_twice_from_fresh_factories():
    # Guards against state leaking between create_app() calls (e.g. a shared container).
    for _ in range(2):
        assert await run_lifespan(create_app()) == LIFESPAN_OK
