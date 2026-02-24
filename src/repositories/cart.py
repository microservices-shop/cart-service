from uuid import UUID

from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import CartItemModel


class CartRepository:
    """SQL-операции над cart_items."""

    @staticmethod
    async def get_by_user(session: AsyncSession, user_id: UUID) -> list[CartItemModel]:
        """Получить все позиции корзины пользователя."""
        query = (
            select(CartItemModel)
            .where(CartItemModel.user_id == user_id)
            .order_by(CartItemModel.created_at)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def delete_all(session: AsyncSession, user_id: UUID) -> int:
        """Очистить корзину пользователя. Возвращает количество удалённых строк."""
        query = (
            delete(CartItemModel)
            .where(CartItemModel.user_id == user_id)
        )
        result = await session.execute(query)
        return result.rowcount

    @staticmethod
    async def mark_price_changed(
        session: AsyncSession,
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
        result = await session.execute(query)
        return result.rowcount

    @staticmethod
    async def mark_out_of_stock(
        session: AsyncSession, product_id: int, value: bool
    ) -> int:
        """Установить или сбросить флаг out_of_stock для всех позиций с product_id."""
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(out_of_stock=value)
        )
        result = await session.execute(query)
        return result.rowcount

    @staticmethod
    async def mark_deleted(session: AsyncSession, product_id: int) -> int:
        """Пометить все позиции с product_id как удалённые."""
        query = (
            update(CartItemModel)
            .where(CartItemModel.product_id == product_id)
            .values(product_deleted=True)
        )
        result = await session.execute(query)
        return result.rowcount
