import uuid
from decimal import Decimal

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import CartItemModel
from src.exceptions import NotFoundException
from src.repositories.cart import CartRepository
from src.schemas.cart import CartItemResponseSchema, CartResponseSchema
from src.services.product_client import ProductClient


logger = structlog.get_logger(__name__)


class CartService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CartRepository(session)
        self.product_client = ProductClient()

    # ─── Public API (v1) ─────────────────────────────────────────

    async def get_cart(self, user_id: uuid.UUID) -> CartResponseSchema:
        """
        Получить корзину пользователя.

        Возвращает список товаров из снапшотов с флагами изменений,
        общую стоимость и общее количество единиц товара.
        Если цена изменилась — для подсчёта total_price используется current_price.
        """
        items = await self.repo.get_by_user(user_id)

        item_responses = [CartItemResponseSchema.model_validate(item) for item in items]

        total_price = Decimal(0)
        total_items = 0
        for item in items:
            effective_price = (
                item.current_price
                if item.price_changed and item.current_price is not None
                else item.product_price
            )
            total_price += effective_price * item.quantity
            total_items += item.quantity

        logger.info("cart_fetched", user_id=str(user_id), items_count=len(items))

        return CartResponseSchema(
            items=item_responses,
            total_price=total_price,
            total_items=total_items,
        )

    async def add_item(
        self, user_id: uuid.UUID, product_id: int, quantity: int
    ) -> CartItemResponseSchema:
        """
        Добавить товар в корзину.

        Если товар уже есть — увеличивает quantity.
        Иначе запрашивает снапшот у Product Service и создаёт новую запись.

        Raises:
            NotFoundException: товар не найден в Product Service
            ServiceUnavailableException: Product Service недоступен
        """
        existing_item = await self.repo.get_by_user_and_product(user_id, product_id)

        if existing_item is not None:
            logger.info(
                "cart_item_duplicate_quantity_increased",
                user_id=str(user_id),
                product_id=product_id,
                new_quantity=existing_item.quantity + quantity,
            )
            updated = await self.repo.update_quantity(
                existing_item, existing_item.quantity + quantity
            )
            await self.session.commit()
            return CartItemResponseSchema.model_validate(updated)

        # Запрашиваем снапшот товара у Product Service
        product = await self.product_client.get_product(product_id)
        product_image = product.images[0] if product.images else None

        item = CartItemModel(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity,
            product_name=product.title,
            product_price=Decimal(product.price),
            product_image=product_image,
        )
        created = await self.repo.create(item)
        await self.session.commit()

        logger.info(
            "cart_item_added",
            user_id=str(user_id),
            product_id=product_id,
            quantity=quantity,
        )
        return CartItemResponseSchema.model_validate(created)

    async def update_quantity(
        self, user_id: uuid.UUID, item_id: uuid.UUID, quantity: int
    ) -> CartItemResponseSchema:
        """
        Изменить количество товара в корзине.

        Raises:
            NotFoundException: запись не найдена или не принадлежит пользователю
        """
        item = await self.repo.get_item(item_id, user_id)
        if item is None:
            raise NotFoundException(
                f"Cart item with id={item_id} not found for user={user_id}"
            )

        updated = await self.repo.update_quantity(item, quantity)
        await self.session.commit()

        logger.info(
            "cart_item_quantity_updated",
            user_id=str(user_id),
            item_id=str(item_id),
            quantity=quantity,
        )
        return CartItemResponseSchema.model_validate(updated)

    async def remove_item(self, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
        """
        Удалить товар из корзины.

        Raises:
            NotFoundException: запись не найдена или не принадлежит пользователю
        """
        item = await self.repo.get_item(item_id, user_id)
        if item is None:
            raise NotFoundException(
                f"Cart item with id={item_id} not found for user={user_id}"
            )

        await self.repo.delete_item(item)
        await self.session.commit()

        logger.info(
            "cart_item_removed",
            user_id=str(user_id),
            item_id=str(item_id),
        )

    async def clear_cart(self, user_id: uuid.UUID) -> None:
        """Очистить всю корзину пользователя."""
        await self.repo.delete_all(user_id)
        await self.session.commit()

        logger.info("cart_cleared", user_id=str(user_id))

    # ─── Internal API (webhooks + Order Service) ──────────────────

    async def get_user_cart(self, user_id: uuid.UUID) -> list[CartItemModel]:
        """Получить корзину пользователя (используется Order Service)."""
        items = await self.repo.get_by_user(user_id)

        logger.info(
            "cart_retrieved",
            user_id=str(user_id),
            items_count=len(items),
        )
        return items

    async def clear_user_cart(self, user_id: uuid.UUID) -> int:
        """Очистить корзину пользователя. Возвращает количество удалённых строк."""
        deleted = await self.repo.delete_all(user_id)
        await self.session.commit()

        logger.info(
            "cart_cleared",
            user_id=str(user_id),
            deleted_rows=deleted,
        )
        return deleted

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
        rows = await self.repo.mark_price_changed(
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
        rows = await self.repo.mark_out_of_stock(product_id, value=True)
        await self.session.commit()

        logger.info(
            "product_out_of_stock_handled",
            product_id=product_id,
            affected_rows=rows,
        )
        return rows

    async def handle_back_in_stock(self, product_id: int) -> int:
        """Обработать webhook 'товар снова в наличии'."""
        rows = await self.repo.mark_out_of_stock(product_id, value=False)
        await self.session.commit()

        logger.info(
            "product_back_in_stock_handled",
            product_id=product_id,
            affected_rows=rows,
        )
        return rows

    async def handle_product_deleted(self, product_id: int) -> int:
        """Обработать webhook 'товар удалён'."""
        rows = await self.repo.mark_deleted(product_id)
        await self.session.commit()

        logger.info(
            "product_deleted_handled",
            product_id=product_id,
            affected_rows=rows,
        )
        return rows
