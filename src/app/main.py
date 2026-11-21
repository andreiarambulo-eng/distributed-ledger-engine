from contextlib import asynccontextmanager
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.di import create_container
from app.domain.exceptions import DomainError, EntityNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = create_container()
    setup_dishka(container, app)
    yield
    await container.close()


def create_app() -> FastAPI:
    """FastAPI application factory."""
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

    # Domain Exception Handlers
    @application.exception_handler(EntityNotFoundError)
    async def handle_entity_not_found(request: Request, exc: EntityNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"code": "NOT_FOUND", "message": exc.message}},
        )

    @application.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"code": "DOMAIN_ERROR", "message": exc.message}},
        )

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
