"""Зависимости FastAPI для Cart Service."""

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import async_session_maker
from src.services.cart import CartService


async def get_db() -> AsyncSession:
    """Открывает сессию БД и закрывает после запроса."""
    async with async_session_maker() as session:
        yield session


def get_user_id(x_user_id: str | None = Header(None)) -> uuid.UUID:
    """Извлекает UUID пользователя из заголовка X-User-ID.

    В продакшене заголовок устанавливается API Gateway после проверки JWT.
    Пока Gateway не реализован - фронтенд передаёт заголовок напрямую.

    Raises:
        HTTPException: 401, если заголовок отсутствует или содержит невалидный UUID.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-ID header is required",
        )

    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-ID header must be a valid UUID",
        )


def get_cart_service(session: Annotated[AsyncSession, Depends(get_db)]) -> CartService:
    """Фабрика для создания сервиса корзины."""
    return CartService(session)


SessionDep = Annotated[AsyncSession, Depends(get_db)]
UserIdDep = Annotated[uuid.UUID, Depends(get_user_id)]
CartServiceDep = Annotated[CartService, Depends(get_cart_service)]
