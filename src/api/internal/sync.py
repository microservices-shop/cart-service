from fastapi import APIRouter, status

from src.api.dependencies import CartServiceDep
from src.schemas.internal import ProductUpdatedWebhook, WebhookResponseSchema

router = APIRouter(prefix="/cart/products", tags=["Internal — Product Sync"])


@router.post(
    "/{product_id}/updated",
    status_code=status.HTTP_200_OK,
    summary="[Internal] Webhook — товар обновлён",
)
async def product_updated(
    product_id: int,
    data: ProductUpdatedWebhook,
    cart_service: CartServiceDep,
) -> WebhookResponseSchema:
    """
    Webhook от Product Service: товар обновлён.

    Обновляет снапшоты во всех позициях корзины с данным product_id.
    Устанавливает price_changed = true если цена отличается от снапшота.
    """
    rows = await cart_service.handle_product_updated(
        product_id=product_id,
        new_price=data.price,
        new_name=data.title,
        new_image=data.image_url,
    )
    return WebhookResponseSchema(affected_rows=rows)


@router.post(
    "/{product_id}/out-of-stock",
    status_code=status.HTTP_200_OK,
    summary="[Internal] Webhook — товар закончился",
)
async def product_out_of_stock(
    product_id: int,
    cart_service: CartServiceDep,
) -> WebhookResponseSchema:
    """
    Webhook от Product Service: stock товара стал 0.

    Устанавливает out_of_stock = true для всех позиций корзины с данным product_id.
    """
    rows = await cart_service.handle_out_of_stock(product_id)
    return WebhookResponseSchema(affected_rows=rows)


@router.post(
    "/{product_id}/back-in-stock",
    status_code=status.HTTP_200_OK,
    summary="[Internal] Webhook — товар снова в наличии",
)
async def product_back_in_stock(
    product_id: int,
    cart_service: CartServiceDep,
) -> WebhookResponseSchema:
    """
    Webhook от Product Service: stock товара снова > 0.

    Сбрасывает out_of_stock = false для всех позиций корзины с данным product_id.
    """
    rows = await cart_service.handle_back_in_stock(product_id)
    return WebhookResponseSchema(affected_rows=rows)


@router.post(
    "/{product_id}/deleted",
    status_code=status.HTTP_200_OK,
    summary="[Internal] Webhook — товар удалён",
)
async def product_deleted(
    product_id: int,
    cart_service: CartServiceDep,
) -> WebhookResponseSchema:
    """
    Webhook от Product Service: товар удалён из каталога.

    Устанавливает product_deleted = true для всех позиций корзины с данным product_id.
    """
    rows = await cart_service.handle_product_deleted(product_id)
    return WebhookResponseSchema(affected_rows=rows)
