from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.v1.user_routes import user_router
from api.v1.user_token_routes import router
from config import Config

app = FastAPI()
Instrumentator().instrument(app).expose(app)
app.include_router(router)
app.include_router(user_router)

if Config.ALLOW_ALL_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    if 'msg' in error:
        error_msg = error["msg"]
    else:
        error_msg = "Unknown error"

    return JSONResponse(
        status_code=422,
        content={"error": error_msg},
    )
