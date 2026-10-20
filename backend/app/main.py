"""FastAPI application factory.

Business routes require a bearer token. Do not publish the API without JWT_SECRET
and DATABASE_URL configured. Production startup refuses a missing or placeholder secret.
A loopback API_HOST does not allow Uvicorn to bind a public address without that secret.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.core.bind import enforce_server_bind
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    # Covers uvicorn.run(app) after this module was imported outside Uvicorn.
    enforce_server_bind()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    # Covers `uvicorn app.main:app`, including --lifespan off, because Uvicorn
    # imports this module while its Config is still on the stack and before it accepts.
    enforce_server_bind(settings)
    show_docs = settings.app_env != "production" or settings.enable_api_docs
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "CivicLens AI API. Business routes require a bearer access token. "
            "No model inference is performed."
        ),
        lifespan=_lifespan,
        docs_url="/docs" if show_docs else None,
        redoc_url="/redoc" if show_docs else None,
        openapi_url="/openapi.json" if show_docs else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    register_exception_handlers(app)
    return app


app = create_app()
