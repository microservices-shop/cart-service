import asyncio

import httpx
import structlog

from src.config import settings
from src.exceptions import NotFoundException, ServiceUnavailableException
from src.schemas.product import ProductResponseSchema

logger = structlog.get_logger(__name__)


# Параметры ретрая
_MAX_RETRIES = 3
_RETRY_BACKOFF_BASE = 0.5  # секунды: 0.5 → 1.0 → 2.0


class ProductClient:
    """Клиент для запросов к internal API Product Service."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._base_url = settings.PRODUCT_SERVICE_URL.rstrip("/")
        self.client = client

    async def get_product(self, product_id: int) -> ProductResponseSchema:
        """
        Получить данные товара из Product Service.

        Запрашивает GET /internal/products/{product_id}.
        При сетевых ошибках выполняет до 3 попыток с экспоненциальным backoff.
        Возвращает ProductResponseSchema.
        """
        url = f"{self._base_url}/internal/products/{product_id}"
        last_exc: Exception | None = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = await self.client.get(url)

                if response.status_code == httpx.codes.NOT_FOUND:
                    raise NotFoundException(
                        f"Product with id={product_id} not found in Product Service"
                    )

                response.raise_for_status()
                return ProductResponseSchema.model_validate(response.json())

            except NotFoundException:
                # 404 — детерминированная ошибка, ретрай бессмысленен
                raise

            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                logger.warning(
                    "product_service_unavailable_retry",
                    product_id=product_id,
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                    error=str(exc),
                )
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_BACKOFF_BASE * (2 ** (attempt - 1)))

            except httpx.HTTPStatusError as exc:
                logger.error(
                    "product_service_error",
                    product_id=product_id,
                    status_code=exc.response.status_code,
                    error=str(exc),
                )
                raise ServiceUnavailableException(
                    f"Product Service returned error: {exc.response.status_code}"
                )

        logger.error(
            "product_service_unavailable",
            product_id=product_id,
            attempts=_MAX_RETRIES,
            error=str(last_exc),
        )
        raise ServiceUnavailableException(
            f"Product Service is temporarily unavailable: {last_exc}"
        )
