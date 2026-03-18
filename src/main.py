from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager
import httpx

from src.api.v1.router import router as v1_router
from src.api.internal.router import internal_router
from src.config import settings
from src.logger import setup_logging, get_logger
from src.middleware.request_logger import RequestLoggingMiddleware
from src.exceptions import NotFoundException, ServiceUnavailableException
from src.services.product_client import ProductClient

logger = get_logger(__name__)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация HTTP клиента для Connection Pooling
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(timeout=10.0, connect=5.0))
    app.state.product_client = ProductClient(http_client)
    yield
    await http_client.aclose()


app = FastAPI(
    title="Cart Service",
    description="Microservice for shopping cart management and product synchronization",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(RequestLoggingMiddleware)

# Подключение публичного API (v1)
app.include_router(v1_router)

# Подключение internal API (webhooks, Order Service)
app.include_router(internal_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cart-service"}


@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail, "error_type": "not_found"},
    )


@app.exception_handler(ServiceUnavailableException)
async def service_unavailable_handler(
    request: Request, exc: ServiceUnavailableException
):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": exc.detail, "error_type": "service_unavailable"},
    )


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
