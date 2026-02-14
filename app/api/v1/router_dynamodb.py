"""
API v1 Router - DynamoDB Version
Combines all route modules for DynamoDB backend
"""
from fastapi import APIRouter

from app.api.v1.routes import auth_dynamodb

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_dynamodb.router)

# Note: Scan, routine, and chat routers would be added here
# For now, auth is implemented to demonstrate the DynamoDB pattern
# You can add the other routers following the same repository pattern
