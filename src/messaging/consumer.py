import structlog
from faststream.rabbit import RabbitRouter

from src.messaging.broker import cart_items_remove_queue
from src.messaging.schemas import CartItemsRemoveMessageSchema
from src.db.database import async_session_maker
from src.services.cart import CartService

logger = structlog.get_logger(__name__)

router = RabbitRouter()


@router.subscriber(cart_items_remove_queue)
async def cart_items_remove_subscriber(msg: CartItemsRemoveMessageSchema):
    logger.info(
        "processing_cart_items_remove",
        order_id=str(msg.order_id),
        user_id=str(msg.user_id),
        message_id=str(msg.message_id),
    )
    try:
        async with async_session_maker() as session:
            cart_service = CartService(session)
            products_ids = [item.product_id for item in msg.items]
            deleted_count = await cart_service.delete_selected_items(
                user_id=msg.user_id, items=products_ids
            )
    except Exception as e:
        logger.error(
            "cart_items_remove_failed", order_id=str(msg.order_id), error=str(e)
        )
        raise

    logger.info(
        "cart_items_remove_processed",
        order_id=str(msg.order_id),
        user_id=str(msg.user_id),
        deleted_rows=deleted_count,
    )
