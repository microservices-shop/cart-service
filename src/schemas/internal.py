import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductUpdatedWebhook(BaseModel):
    """Схема входящего webhook'а при обновлении товара в Product Service."""

    title: str = Field(..., description="Актуальное название товара")
    price: int = Field(..., description="Актуальная цена в копейках")
    image_url: str | None = Field(None, description="URL первого изображения товара")


class InternalCartItemSchema(BaseModel):
    """Элемент корзины — используется Order Service при оформлении заказа."""

    id: uuid.UUID = Field(..., description="ID записи корзины")
    product_id: int = Field(..., description="ID товара в Product Service")
    quantity: int = Field(..., description="Количество товара")
    product_name: str = Field(..., description="Название товара")
    product_price: Decimal = Field(..., description="Цена товара на момент добавления")
    product_image: str | None = Field(None, description="URL изображения товара")
    price_changed: bool = Field(
        ..., description="True если цена изменилась с момента добавления"
    )
    current_price: Decimal | None = Field(
        None, description="Актуальная цена (если изменилась)"
    )
    out_of_stock: bool = Field(..., description="True если товар закончился на складе")
    product_deleted: bool = Field(..., description="True если товар удалён из каталога")

    model_config = ConfigDict(from_attributes=True)


class WebhookResponseSchema(BaseModel):
    """Стандартный ответ webhook-эндпоинта."""

    status: str = Field("ok", description="Статус обработки")
    affected_rows: int = Field(..., description="Количество затронутых строк")
