from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import Response

from src.api.dependencies import CartServiceDep, UserIdDep
from src.schemas.cart import CartItemSelectedResponseSchema
from src.schemas.internal import InternalCartItemSchema

router = APIRouter(prefix="/cart", tags=["Internal — Cart"])


@router.get(
    "/selected",
    status_code=status.HTTP_200_OK,
    summary="Получить выбранные товары из корзины",
)
async def get_selected_internal(
    user_id: UserIdDep,
    cart_service: CartServiceDep,
) -> list[CartItemSelectedResponseSchema]:
    """
    Получить только выбранные товары из корзины.

    Используется Order Service при оформлении заказа.
    """
    return await cart_service.get_list_selected_items(user_id)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить корзину пользователя",
)
async def get_cart_internal(
    user_id: UUID,
    cart_service: CartServiceDep,
) -> list[InternalCartItemSchema]:
    """
    Получить содержимое корзины пользователя.

    Используется Order Service при оформлении заказа.
    """
    items = await cart_service.get_user_cart(user_id)

    return [InternalCartItemSchema.model_validate(item) for item in items]


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить корзину пользователя",
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
