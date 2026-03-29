from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    garmin_connected: bool = False

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, user):
        """Custom from_orm to add computed fields."""
        data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "garmin_connected": bool(user.garmin_oauth1_token),
        }
        return cls(**data)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GarminConnect(BaseModel):
    email: str
    password: str
