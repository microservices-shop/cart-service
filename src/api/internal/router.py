from fastapi import APIRouter

from src.api.internal import sync, cart

internal_router = APIRouter(prefix="/internal")
internal_router.include_router(sync.router)
internal_router.include_router(cart.router)
