from pydantic import BaseModel, Field


class ProductUpdatedWebhook(BaseModel):
    """Схема входящего webhook'а при обновлении товара в Product Service."""

    title: str = Field(..., description="Актуальное название товара")
    price: int = Field(..., description="Актуальная цена в копейках")
    image_url: str | None = Field(None, description="URL первого изображения товара")
