from contextlib import asynccontextmanager

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.di import create_container
from app.domain.exceptions import AuthenticationError, DomainError, EntityNotFoundError

# Domain exception -> (HTTP status, error code). Starlette picks the handler by walking the
# exception's MRO, so DomainError only catches subclasses that have no entry of their own.
DOMAIN_ERROR_RESPONSES: dict[type[DomainError], tuple[int, str]] = {
    AuthenticationError: (status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED"),
    EntityNotFoundError: (status.HTTP_404_NOT_FOUND, "NOT_FOUND"),
    DomainError: (status.HTTP_400_BAD_REQUEST, "DOMAIN_ERROR"),
}


def _domain_error_handler(status_code: int, code: str):
    async def handle(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"error": {"code": code, "message": exc.message}},
        )

    return handle


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Releases APP-scoped resources (DB pool, clients) that were opened on first use.
    await app.state.dishka_container.close()


def create_app(container: AsyncContainer | None = None) -> FastAPI:
    """FastAPI application factory.

    Pass `container` to swap dependencies (tests); by default the real one is built.
    """
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Dependency injection. Must happen here, not in lifespan: Dishka installs a middleware,
    # and Starlette rejects new middleware once the app has started. Building the container
    # is lazy, so no connections are opened until a dependency is first resolved.
    setup_dishka(container or create_container(), application)

    # Domain Exception Handlers
    for exc_type, (status_code, code) in DOMAIN_ERROR_RESPONSES.items():
        application.add_exception_handler(exc_type, _domain_error_handler(status_code, code))

    # Register Routers
    application.include_router(api_v1_router)

    @application.get("/", include_in_schema=False)
    async def root():
        return {
            "service": settings.app_name,
            "version": "0.1.0",
            "docs_url": "/docs",
        }

    return application


app = create_app()
