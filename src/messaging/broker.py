import asyncio
from faststream.rabbit import RabbitBroker, RabbitQueue
from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)

broker = RabbitBroker(settings.RABBITMQ_URL)

cart_items_remove_queue = RabbitQueue(
    "cart.items.remove",
    durable=True,
)

_MAX_RETRIES = 5


async def connect_broker() -> None:
    """Подключение к RabbitMQ с retry и экспоненциальным backoff."""
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            await broker.connect()
            await broker.start()
            logger.info("rabbitmq_broker_connected")
            return
        except Exception as e:
            if attempt == _MAX_RETRIES:
                logger.critical("rabbitmq_broker_connect_failed", error=str(e))
                raise
            logger.warning(
                "rabbitmq_broker_retry",
                attempt=attempt,
                max_retries=_MAX_RETRIES,
                error=str(e),
            )
            await asyncio.sleep(2**attempt)
