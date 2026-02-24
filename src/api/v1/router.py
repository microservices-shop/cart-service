from fastapi import APIRouter

from src.api.v1.cart import router as cart_router

router = APIRouter(prefix="/api/v1")
router.include_router(cart_router)
