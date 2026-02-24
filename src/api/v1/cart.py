"""Публичные эндпоинты корзины пользователя."""

import uuid

from fastapi import APIRouter, status

from src.api.dependencies import CartServiceDep, UserIdDep
from src.schemas.cart import (
    AddToCartSchema,
    CartItemResponseSchema,
    CartResponseSchema,
    UpdateQuantitySchema,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_cart(
    user_id: UserIdDep,
    service: CartServiceDep,
) -> CartResponseSchema:
    """Получить корзину текущего пользователя со снапшотами и флагами изменений."""
    return await service.get_cart(user_id)


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Товар не найден в Product Service"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Product Service недоступен"
        },
    },
)
async def add_item(
    body: AddToCartSchema,
    user_id: UserIdDep,
    service: CartServiceDep,
) -> CartItemResponseSchema:
    """Добавить товар в корзину.

    Если товар уже есть — увеличивает количество.
    Запрашивает снапшот данных у Product Service.

    Raises:
        HTTPException: 404, если товар не найден в Product Service.
        HTTPException: 503, если Product Service недоступен.
    """
    return await service.add_item(user_id, body.product_id, body.quantity)


@router.patch(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Позиция не найдена или не принадлежит пользователю"
        },
    },
)
async def update_quantity(
    item_id: uuid.UUID,
    body: UpdateQuantitySchema,
    user_id: UserIdDep,
    service: CartServiceDep,
) -> CartItemResponseSchema:
    """Изменить количество товара в корзине.

    Raises:
        HTTPException: 404, если позиция не найдена или не принадлежит пользователю.
    """
    return await service.update_quantity(user_id, item_id, body.quantity)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Позиция не найдена или не принадлежит пользователю"
        },
    },
)
async def remove_item(
    item_id: uuid.UUID,
    user_id: UserIdDep,
    service: CartServiceDep,
) -> None:
    """Удалить конкретный товар из корзины.

    Raises:
        HTTPException: 404, если позиция не найдена или не принадлежит пользователю.
    """
    await service.remove_item(user_id, item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    user_id: UserIdDep,
    service: CartServiceDep,
) -> None:
    """Очистить всю корзину пользователя."""
    await service.clear_cart(user_id)
