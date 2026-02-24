from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from src.config import settings
from src.logger import setup_logging, get_logger
from src.middleware.request_logger import RequestLoggingMiddleware

logger = get_logger(__name__)

setup_logging()

app = FastAPI(
    title="Cart Service",
    description="Microservice for shopping cart management and product synchronization",
    version="0.1.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(RequestLoggingMiddleware)

# Подключение internal API
from src.api.internal.router import internal_router

app.include_router(internal_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cart-service"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # request_id АВТОМАТИЧЕСКИ добавляется в логи из контекста structlog
    logger.exception("unhandled_exception")
    request_id = structlog.contextvars.get_contextvars().get("request_id")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please report this ID to support.",
            "request_id": request_id,
        },
    )
