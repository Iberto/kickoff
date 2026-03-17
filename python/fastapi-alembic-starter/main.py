from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from structlog.stdlib import BoundLogger

# application stuff
from src.config import settings
from src.exceptions.base import (
    generic_exception_handler,
    rate_limit_exceeded_handler,
    starter_exception_handler,
)
from src.exceptions.users import StarterBaseException
from src.limiter import limiter
from src.logging import setup_logging
from src.middleware import RequestContextMiddleware

# endpoints
from src.routes.users import router as user_router

logger: BoundLogger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""

    # === STARTUP: before yield ===
    # Here:
    # - connection to db pool
    # - Initialize cache
    # - Warmup services
    logger.info("starting_server")
    # Logger
    setup_logging()

    # Server
    yield

    # === SHUTDOWN: after yeld ===
    # Here:
    # - Close db session
    # - Flush cache
    # - Cleanup
    # TODO: shutdown database connection
    logger.info("shutting_server")


def create_app() -> FastAPI:
    """Application factory"""

    app = FastAPI(
        title="src",
        description="My trading app",
        version="0.1.0",  # TODO: get it from configuration or env
        lifespan=lifespan,
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
    )

    # Middlewares: note that order matters - first added -> outermost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    # Exc handler
    app.add_exception_handler(StarterBaseException, starter_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Routes
    app.include_router(user_router)

    # limiter
    app.state.limiter = limiter

    return app


app = create_app()
