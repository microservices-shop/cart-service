from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import Response

from src.api.dependencies import CartServiceDep

router = APIRouter(prefix="/cart", tags=["Internal — Cart"])


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="[Internal] Получить корзину пользователя",
)
async def get_cart_internal(
    user_id: UUID,
    cart_service: CartServiceDep,
) -> list[dict]:
    """
    Получить содержимое корзины пользователя.

    Используется Order Service при оформлении заказа.
    """
    items = await cart_service.get_user_cart(user_id)

    return [
        {
            "id": str(item.id),
            "product_id": item.product_id,
            "quantity": item.quantity,
            "product_name": item.product_name,
            "product_price": float(item.product_price),
            "product_image": item.product_image,
            "price_changed": item.price_changed,
            "current_price": float(item.current_price)
            if item.current_price is not None
            else None,
            "out_of_stock": item.out_of_stock,
            "product_deleted": item.product_deleted,
        }
        for item in items
    ]


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Internal] Очистить корзину пользователя",
)
async def clear_cart_internal(
    user_id: UUID,
    cart_service: CartServiceDep,
) -> Response:
    """
    Очистить корзину пользователя.

    Используется Order Service после успешного оформления заказа.
    """
    await cart_service.clear_user_cart(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
