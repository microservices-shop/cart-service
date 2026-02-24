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
        query = (
            select(CartItemModel)
            .where(CartItemModel.user_id == user_id)
            .order_by(CartItemModel.created_at)
        )
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

    async def delete_all(self, user_id: uuid.UUID) -> int:
        """Очистка всей корзины пользователя. Возвращает количество удалённых строк."""
        query = delete(CartItemModel).where(CartItemModel.user_id == user_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def mark_price_changed(
        self,
        product_id: int,
        new_price: int,
        new_name: str,
        new_image: str | None,
    ) -> int:
        """
        Обновить снапшоты всех позиций с данным product_id.

        Устанавливает price_changed = true если новая цена отличается от
        сохранённой в снапшоте.
        Возвращает количество затронутых строк.
        """
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(
                current_price=new_price,
                price_changed=CartItemModel.product_price != new_price,
                product_name=new_name,
                product_image=new_image,
            )
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def mark_out_of_stock(self, product_id: int, value: bool) -> int:
        """Установить или сбросить флаг out_of_stock для всех позиций с product_id."""
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(out_of_stock=value)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def mark_deleted(self, product_id: int) -> int:
        """Пометить все позиции с product_id как удалённые."""
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(product_deleted=True)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def update_by_product_id(self, product_id: int, **fields: Any) -> None:
        """Массовое обновление всех записей с указанным product_id (для webhook'ов)."""
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(**fields)
        )
        await self.session.execute(query)
        await self.session.flush()
