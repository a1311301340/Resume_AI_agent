from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail if isinstance(exc.detail, str) else "request failed",
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"internal error: {exc}",
                "data": None,
            },
        )

