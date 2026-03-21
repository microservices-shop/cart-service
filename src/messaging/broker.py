from faststream.rabbit import RabbitBroker, RabbitQueue
from src.config import settings

broker = RabbitBroker(settings.RABBITMQ_URL)

cart_items_remove_queue = RabbitQueue(
    "cart.items.remove",
    durable=True,
)
