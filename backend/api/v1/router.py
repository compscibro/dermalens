"""
API v1 Router — combines all route modules
"""
from fastapi import APIRouter

from backend.api.v1.routes import users, scans, routines, chat

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(scans.router)
api_router.include_router(routines.router)
api_router.include_router(chat.router)
