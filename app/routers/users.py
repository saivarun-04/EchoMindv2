"""User profile and activity endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import MemoryLog, User

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class UserProfileOut(BaseModel):
    id: int
    name: str
    email: str
    bio: str
    profile_image: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    profile_image: Optional[str] = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters.")
        return v


class MemoryLogOut(BaseModel):
    id: int
    content: str
    platform: str
    hindsight_bank: str
    created_at: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserProfileOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get the authenticated user's profile from SQLite.
    Protected by JWT.
    """
    return UserProfileOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        bio=current_user.bio or "",
        profile_image=current_user.profile_image or "",
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else "",
    )


@router.put("/me", response_model=UserProfileOut)
def update_my_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated user's profile in SQLite.
    Persists changes to `name`, `bio`, and `profile_image`.
    """
    if data.name is not None:
        current_user.name = data.name
    if data.bio is not None:
        current_user.bio = data.bio.strip()
    if data.profile_image is not None:
        current_user.profile_image = data.profile_image.strip()

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return UserProfileOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        bio=current_user.bio or "",
        profile_image=current_user.profile_image or "",
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else "",
    )


@router.get("/me/memories", response_model=List[MemoryLogOut])
def get_my_memory_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve all memories logged in SQLite by this user.
    Demonstrates the direct User -> SQLite memory_logs relationship.
    """
    logs = (
        db.query(MemoryLog)
        .filter(MemoryLog.user_id == current_user.id)
        .order_by(MemoryLog.created_at.desc())
        .all()
    )
    return [
        MemoryLogOut(
            id=log.id,
            content=log.content,
            platform=log.platform or "general",
            hindsight_bank=log.hindsight_bank or "social-audience",
            created_at=log.created_at.isoformat() if log.created_at else "",
        )
        for log in logs
    ]
