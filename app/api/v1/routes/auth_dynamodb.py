"""
Authentication router - DynamoDB version
Handles user registration, login, and profile management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any

from app.repositories.user_repository import user_repository
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdate,
    PasswordChange
)
from app.core.security import create_access_token, get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await user_repository.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            skin_type=user_data.skin_type,
            primary_concern=user_data.primary_concern
        )
        
        # Generate access token
        access_token = create_access_token(data={"sub": user['user_id']})
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse(**user)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user and return access token"""
    user = await user_repository.authenticate_user(
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user['user_id']})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(**user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get current user profile"""
    user = await user_repository.get_user_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.pop('hashed_password', None)
    return UserResponse(**user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user profile"""
    user = await user_repository.update_user(
        user_id=current_user_id,
        full_name=update_data.full_name,
        skin_type=update_data.skin_type,
        primary_concern=update_data.primary_concern
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user_id: str = Depends(get_current_user_id)
):
    """Change user password"""
    success = await user_repository.change_password(
        user_id=current_user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    return {"message": "Password updated successfully"}
