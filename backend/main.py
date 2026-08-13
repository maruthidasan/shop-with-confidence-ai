import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from middleware.request_context import RequestContextMiddleware
from routers import health_router, recommendation_router, tryon_router, upload_router
from schemas.common import ErrorResponse
from utils.logging import configure_logging
from services.errors import ProviderConfigurationError, ProviderError

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0", debug=settings.debug, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(RequestContextMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

app.include_router(health_router.router)
app.include_router(upload_router.router)
app.include_router(recommendation_router.router)
app.include_router(tryon_router.router)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    payload = ErrorResponse(message=str(exc), errorCode="INVALID_REQUEST", requestId=request_id)
    return JSONResponse(status_code=400, content=payload.model_dump(by_alias=True))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.warning("validation_error request_id=%s errors=%s", request_id, exc.errors())
    payload = ErrorResponse(message="Request validation failed.", errorCode="VALIDATION_ERROR", requestId=request_id)
    return JSONResponse(status_code=422, content=payload.model_dump(by_alias=True))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    payload = ErrorResponse(message=str(exc.detail), errorCode="REQUEST_REJECTED", requestId=request_id)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(by_alias=True))


@app.exception_handler(ProviderConfigurationError)
async def provider_configuration_handler(request: Request, exc: ProviderConfigurationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    payload = ErrorResponse(message="This styling service is being prepared. Please try again shortly.", errorCode="SERVICE_CONFIGURATION", requestId=request_id)
    return JSONResponse(status_code=503, content=payload.model_dump(by_alias=True))


@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    payload = ErrorResponse(message=str(exc), errorCode="STYLIST_UNAVAILABLE", requestId=request_id)
    return JSONResponse(status_code=503, content=payload.model_dump(by_alias=True))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_error request_id=%s", request_id)
    payload = ErrorResponse(message="An unexpected error occurred.", errorCode="INTERNAL_ERROR", requestId=request_id)
    return JSONResponse(status_code=500, content=payload.model_dump(by_alias=True))
