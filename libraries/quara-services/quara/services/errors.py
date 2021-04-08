from typing import Any, Callable

from fastapi import FastAPI
from quara.api import logger
from quara.core.errors import (
    InvalidDocumentId,
    InvalidMessageDataError,
    InvalidMessageError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from starlette.requests import Request
from starlette.responses import JSONResponse


def add_catch_exceptions_middleware(app: FastAPI) -> None:
    async def catch_exceptions_middleware(
        request: Request, call_next: Callable[..., Any]
    ) -> Any:
        try:
            return await call_next(request)
        except Exception as err:
            logger.error(err)
            if isinstance(err, (ResourceNotFoundError, InvalidDocumentId)):
                return JSONResponse(
                    {"details": "Resource not found", "error": "ResourceNotFound"},
                    status_code=404,
                )
            if isinstance(err, ResourceAlreadyExistsError):
                return JSONResponse(
                    {
                        "details": "Resource already exist",
                        "error": "ResourceAlreadyExists",
                    },
                    status_code=409,
                )
            if isinstance(err, (InvalidMessageDataError, InvalidMessageError)):
                return JSONResponse(
                    {"details": str(err), "error": "InvalidRequestData"},
                    status_code=428,
                )
            # you probably want some kind of logging here
            return JSONResponse(
                {"details": str(err), "error": type(err).__name__}, status_code=500
            )

    app.middleware("http")(catch_exceptions_middleware)
