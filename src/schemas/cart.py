import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AddToCartSchema(BaseModel):
    product_id: int = Field(..., description="ID товара в Product Service", gt=0)
    quantity: int = Field(1, description="Количество товара", ge=1)


class UpdateQuantitySchema(BaseModel):
    quantity: int = Field(..., description="Новое количество товара", ge=1)


class CartItemResponseSchema(BaseModel):
    """Ответ с данными одного элемента корзины."""

    id: uuid.UUID = Field(..., description="ID записи корзины")
    product_id: int = Field(..., description="ID товара в Product Service")
    quantity: int = Field(..., description="Количество товара")

    # Снапшот товара на момент добавления
    product_name: str = Field(..., description="Название товара на момент добавления")
    product_price: Decimal = Field(..., description="Цена товара на момент добавления")
    product_image: str | None = Field(None, description="URL изображения товара")

    # Флаги синхронизации (обновляются через webhook'и)
    price_changed: bool = Field(
        ..., description="True если цена изменилась с момента добавления"
    )
    current_price: Decimal | None = Field(
        None,
        description="Актуальная цена — заполняется webhook'ом при изменении цены",
    )
    out_of_stock: bool = Field(..., description="True если товар закончился на складе")
    product_deleted: bool = Field(..., description="True если товар удалён из каталога")

    created_at: datetime = Field(..., description="Дата добавления в корзину")
    updated_at: datetime = Field(..., description="Дата последнего изменения")

    model_config = ConfigDict(from_attributes=True)


class CartResponseSchema(BaseModel):
    """Ответ с данными всей корзины пользователя."""

    items: list[CartItemResponseSchema] = Field(
        ..., description="Список товаров в корзине"
    )
    total_price: Decimal = Field(..., description="Общая стоимость корзины")
    total_items: int = Field(..., description="Общее количество единиц товара")
