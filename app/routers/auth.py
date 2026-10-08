"""Authentication endpoints: Signup, Signin, Logout."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------
class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    confirm_password: str = Field(min_length=6, max_length=128)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters.")
        return v

    @field_validator("confirm_password")
    @classmethod
    def _passwords_match(cls, v: str, info) -> str:
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match.")
        return v


class SigninRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    bio: str
    profile_image: str
    created_at: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: str
    user: UserOut


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user:
    - Validate email and password match
    - Reject duplicate email (returns 409 Conflict)
    - Hash password using bcrypt
    - Create user row in SQLite
    - Generate JWT and return authenticated session
    """
    clean_email = str(data.email).strip().lower()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    pw_hash = hash_password(data.password)
    user = User(
        name=data.name,
        email=clean_email,
        password_hash=pw_hash,
        bio="",
        profile_image="",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return AuthResponse(
        success=True,
        message="Account created successfully.",
        token=token,
        user=UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            bio=user.bio or "",
            profile_image=user.profile_image or "",
            created_at=user.created_at.isoformat() if user.created_at else "",
        ),
    )


@router.post("/signin", response_model=AuthResponse)
def signin(data: SigninRequest, db: Session = Depends(get_db)):
    """
    Authenticate user:
    - Look up email safely
    - Verify bcrypt password
    - Generate JWT access token
    - Return user details + token
    """
    clean_email = str(data.email).strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()

    # Generic error message to avoid account harvesting
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id)
    return AuthResponse(
        success=True,
        message="Signed in successfully.",
        token=token,
        user=UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            bio=user.bio or "",
            profile_image=user.profile_image or "",
            created_at=user.created_at.isoformat() if user.created_at else "",
        ),
    )


@router.post("/logout")
def logout():
    """
    Stateless JWT logout:
    Instructs the client to discard the stored token.
    """
    return {"success": True, "message": "Signed out successfully."}
