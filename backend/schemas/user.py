"""
User schemas — matches Swift UserProfile struct
"""
from pydantic import BaseModel
from typing import Optional


class UserProfileSchema(BaseModel):
    id: str
    name: str
    email: str
    username: str
    avatarSystemName: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    avatarSystemName: Optional[str] = None
