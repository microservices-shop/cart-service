import structlog
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import CartItemModel
from src.repositories.cart import CartRepository


logger = structlog.get_logger(__name__)


class CartService:
    """Бизнес-логика корзины."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = CartRepository()

    async def handle_product_updated(
        self,
        product_id: int,
        new_price: int,
        new_name: str,
        new_image: str | None,
    ) -> int:
        """
        Обработать webhook «товар обновлён».

        Обновляет снапшоты и ставит price_changed если цена изменилась.
        Возвращает количество затронутых строк.
        """
        rows = await self._repo.mark_price_changed(
            self.session,
            product_id=product_id,
            new_price=new_price,
            new_name=new_name,
            new_image=new_image,
        )
        await self.session.commit()

        logger.info(
            "product_updated_handled",
            product_id=product_id,
            affected_rows=rows,
            new_price=new_price,
        )
        return rows

    async def handle_out_of_stock(self, product_id: int) -> int:
        """Обработать webhook 'товар закончился'."""
        rows = await self._repo.mark_out_of_stock(self.session, product_id, value=True)
        await self.session.commit()

        logger.info(
            "product_out_of_stock_handled",
            product_id=product_id,
            affected_rows=rows,
        )
        return rows

    async def handle_back_in_stock(self, product_id: int) -> int:
        """Обработать webhook 'товар снова в наличии'."""
        rows = await self._repo.mark_out_of_stock(self.session, product_id, value=False)
        await self.session.commit()

        logger.info(
            "product_back_in_stock_handled",
            product_id=product_id,
            affected_rows=rows,
        )
        return rows

    async def handle_product_deleted(self, product_id: int) -> int:
        """Обработать webhook 'товар удалён'."""
        rows = await self._repo.mark_deleted(self.session, product_id)
        await self.session.commit()

        logger.info(
            "product_deleted_handled",
            product_id=product_id,
            affected_rows=rows,
        )
        return rows

    async def get_user_cart(self, user_id: UUID) -> list[CartItemModel]:
        """Получить корзину пользователя."""
        items = await self._repo.get_by_user(self.session, user_id)

        logger.info(
            "cart_retrieved",
            user_id=str(user_id),
            items_count=len(items),
        )
        return items

    async def clear_user_cart(self, user_id: UUID) -> int:
        """Очистить корзину пользователя. Возвращает количество удалённых строк."""
        deleted = await self._repo.delete_all(self.session, user_id)
        await self.session.commit()

        logger.info(
            "cart_cleared",
            user_id=str(user_id),
            deleted_rows=deleted,
        )
        return deleted
