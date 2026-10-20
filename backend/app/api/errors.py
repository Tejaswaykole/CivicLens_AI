"""Map failures to a stable JSON error body without leaking internals."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.errors import AppError

logger = logging.getLogger(__name__)


def _body(code: str, message: str, details: list[dict] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or []}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_request: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for error in exc.errors():
            details.append(
                {
                    "loc": [str(item) for item in error.get("loc", [])],
                    "message": error.get("msg", "Invalid value"),
                    "type": error.get("type", "value_error"),
                }
            )
        return JSONResponse(
            status_code=422,
            content=_body("validation_error", "Request validation failed.", details),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity(_request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("Database integrity conflict (%s).", type(exc).__name__)
        return JSONResponse(
            status_code=409,
            content=_body("conflict", "The request conflicts with existing data."),
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_database(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.warning("Database request failed (%s).", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content=_body("database_unavailable", "The database is unavailable."),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error (%s).", type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content=_body("internal_error", "The request could not be completed."),
        )
