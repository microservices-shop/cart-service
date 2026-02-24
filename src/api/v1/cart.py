"""Публичные эндпоинты корзины пользователя."""

import uuid

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import CartServiceDep, UserIdDep
from src.exceptions import NotFoundException, ServiceUnavailableException
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


@router.post("/items", status_code=status.HTTP_201_CREATED)
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
    try:
        return await service.add_item(user_id, body.product_id, body.quantity)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ServiceUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.detail
        )


@router.patch("/items/{item_id}", status_code=status.HTTP_200_OK)
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
    try:
        return await service.update_quantity(user_id, item_id, body.quantity)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    item_id: uuid.UUID,
    user_id: UserIdDep,
    service: CartServiceDep,
) -> None:
    """Удалить конкретный товар из корзины.

    Raises:
        HTTPException: 404, если позиция не найдена или не принадлежит пользователю.
    """
    try:
        await service.remove_item(user_id, item_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    user_id: UserIdDep,
    service: CartServiceDep,
) -> None:
    """Очистить всю корзину пользователя."""
    await service.clear_cart(user_id)
