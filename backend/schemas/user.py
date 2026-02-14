"""
User schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None
    skin_type: Optional[str] = Field(None, pattern="^(oily|dry|combination|sensitive)$")
    primary_concern: Optional[str] = Field(None, pattern="^(acne|redness|dryness|oiliness)$")


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    skin_type: Optional[str] = Field(None, pattern="^(oily|dry|combination|sensitive)$")
    primary_concern: Optional[str] = Field(None, pattern="^(acne|redness|dryness|oiliness)$")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
