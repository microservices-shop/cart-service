import uuid
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import CartItemModel


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id: uuid.UUID) -> list[CartItemModel]:
        """Все элементы корзины пользователя."""
        query = select(CartItemModel).where(CartItemModel.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_item(
        self, item_id: uuid.UUID, user_id: uuid.UUID
    ) -> CartItemModel | None:
        """Один элемент корзины с проверкой принадлежности пользователю."""
        query = select(CartItemModel).where(
            CartItemModel.id == item_id,
            CartItemModel.user_id == user_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_and_product(
        self, user_id: uuid.UUID, product_id: int
    ) -> CartItemModel | None:
        """Поиск существующего элемента корзины (проверка дубликата)."""
        query = select(CartItemModel).where(
            CartItemModel.user_id == user_id,
            CartItemModel.product_id == product_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, item: CartItemModel) -> CartItemModel:
        """Создание нового элемента корзины."""
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_quantity(
        self, item: CartItemModel, quantity: int
    ) -> CartItemModel:
        """Обновление количества товара в корзине."""
        item.quantity = quantity
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: CartItemModel) -> None:
        """Удаление одного элемента из корзины."""
        await self.session.delete(item)
        await self.session.flush()

    async def delete_all(self, user_id: uuid.UUID) -> None:
        """Очистка всей корзины пользователя."""
        query = delete(CartItemModel).where(CartItemModel.user_id == user_id)
        await self.session.execute(query)
        await self.session.flush()

    async def update_by_product_id(self, product_id: int, **fields: Any) -> None:
        """Массовое обновление всех записей с указанным product_id (для webhook'ов)."""
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(**fields)
        )
        await self.session.execute(query)
        await self.session.flush()
