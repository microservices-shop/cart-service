from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import async_session_maker
from src.services.cart import CartService


async def get_db() -> AsyncSession:
    """Открывает сессию, отдаёт её и закрывает после запроса."""
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_cart_service(session: SessionDep) -> CartService:
    """Фабрика для создания сервиса корзины."""
    return CartService(session)


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]
