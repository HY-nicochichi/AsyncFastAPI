from fastapi import APIRouter
from .token import token_router
from .user import user_router

routers: list[APIRouter] = [
    token_router,
    user_router
]
