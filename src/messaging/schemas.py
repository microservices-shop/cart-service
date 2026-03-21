import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CartItemRemoveSchema(BaseModel):
    """Схема товара для удаления из корзины."""

    product_id: int = Field(..., description="ID товара")


class CartItemsRemoveMessageSchema(BaseModel):
    """Схема сообщения в очереди cart.items.remove - удаляет купленные товары из корзины."""

    message_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="ID сообщения для дедупликации"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Время отправки"
    )
    order_id: uuid.UUID = Field(..., description="ID заказа")
    user_id: uuid.UUID = Field(..., description="ID пользователя")
    items: list[CartItemRemoveSchema] = Field(
        ..., description="Список товаров для удаления"
    )
