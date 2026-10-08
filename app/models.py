"""SQLAlchemy ORM models for EchoMind application data."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Application user. Passwords are stored as bcrypt hashes — never plaintext."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    bio = Column(Text, default="")
    profile_image = Column(String(500), default="")  # URL to a profile photo
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    memory_logs = relationship(
        "MemoryLog", back_populates="user", cascade="all, delete-orphan"
    )


class MemoryLog(Base):
    """
    Records every experience a user teaches to EchoMind.

    Associates the authenticated user with the content sent to Hindsight,
    providing a per-user activity history stored entirely in SQLite.
    Hindsight remains the AI memory layer; this table is the audit layer.
    """

    __tablename__ = "memory_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    platform = Column(String(50), default="general")
    hindsight_bank = Column(String(100), default="social-audience")
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="memory_logs")
