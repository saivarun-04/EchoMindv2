"""SQLite database setup for EchoMind application data (users, memory logs)."""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Database sits at project root: echomind.db
BASE_DIR = Path(__file__).resolve().parent.parent
_db_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'echomind.db'}")

engine = create_engine(_db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a SQLAlchemy session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
