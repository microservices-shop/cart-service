import httpx
import structlog
from fastapi import status

from src.config import settings
from src.exceptions import NotFoundException, ServiceUnavailableException
from src.schemas.product import ProductResponseSchema

logger = structlog.get_logger(__name__)

# Таймауты: 5 секунд на подключение, 10 на чтение
_TIMEOUT = httpx.Timeout(timeout=10.0, connect=5.0)


class ProductClient:
    """Клиент для запросов к internal API Product Service."""

    def __init__(self) -> None:
        self._base_url = settings.PRODUCT_SERVICE_URL.rstrip("/")

    async def get_product(self, product_id: int) -> ProductResponseSchema:
        """
        Получить данные товара из Product Service.

        Запрашивает GET /internal/products/{product_id}.
        Возвращает ProductResponseSchema.
        """
        url = f"{self._base_url}/internal/products/{product_id}"

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url)

            if response.status_code == status.HTTP_404_NOT_FOUND:
                raise NotFoundException(
                    f"Product with id={product_id} not found in Product Service"
                )

            response.raise_for_status()
            return ProductResponseSchema.model_validate(response.json())

        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            logger.error(
                "product_service_unavailable",
                product_id=product_id,
                error=str(exc),
            )
            raise ServiceUnavailableException(
                "Product Service is temporarily unavailable"
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.error(
                "product_service_error",
                product_id=product_id,
                status_code=exc.response.status_code,
                error=str(exc),
            )
            raise ServiceUnavailableException(
                f"Product Service returned error: {exc.response.status_code}"
            ) from exc
