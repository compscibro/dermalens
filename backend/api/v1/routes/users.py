"""
Users router — profile CRUD via S3
No auth — user identified by email query param.
"""
from fastapi import APIRouter, Query, HTTPException
import uuid

from backend.schemas.user import UserProfileSchema, UserProfileUpdate
from backend.services.storage.s3_service import s3_service

router = APIRouter(prefix="/users", tags=["Users"])


def _require_email(email: str = Query(..., description="User email")) -> str:
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")
    return email


@router.get("/profile", response_model=UserProfileSchema)
def get_profile(email: str = Query(..., description="User email")):
    """Get user profile. Creates a default one if it doesn't exist."""
    email = _require_email(email)
    key = s3_service.profile_key(email)
    data = s3_service.get_json(key)

    if data is None:
        # Auto-create a default profile
        name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "username": email.split("@")[0],
            "avatarSystemName": "person.crop.circle.fill",
        }
        s3_service.put_json(key, data)

    return UserProfileSchema(**data)


@router.put("/profile", response_model=UserProfileSchema)
def update_profile(
    update: UserProfileUpdate,
    email: str = Query(..., description="User email"),
):
    """Update user profile fields."""
    email = _require_email(email)
    key = s3_service.profile_key(email)
    data = s3_service.get_json(key)

    if data is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Merge provided fields
    update_dict = update.model_dump(exclude_none=True)
    data.update(update_dict)
    s3_service.put_json(key, data)

    return UserProfileSchema(**data)
