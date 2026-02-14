"""
API v1 Router
Combines all route modules
"""
from fastapi import APIRouter

from app.api.v1.routes import auth, scans, routines, chat

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(scans.router)
api_router.include_router(routines.router)
api_router.include_router(chat.router)
