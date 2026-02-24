from pydantic import BaseModel, Field


class ProductResponseSchema(BaseModel):
    """Схема ответа от Product Service (internal API)."""

    id: int = Field(..., description="ID товара")
    title: str = Field(..., description="Название товара")
    price: int = Field(..., description="Цена в копейках")
    images: list[str] = Field(
        default_factory=list, description="URL изображений товара"
    )
