from fastapi import APIRouter, Response, status, HTTPException, Depends

from app.auth_service.auth import get_current_user
from app.access.cart import access_cart

cart_router = APIRouter(prefix="/cart", tags=["Корзина"])

@cart_router.get("/{user_id}")
async def get_cart(user_id: int):
    return await access_cart(method="get", id=user_id)