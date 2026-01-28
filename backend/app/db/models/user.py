from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(15), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    guardian_contact: Mapped[Optional[str]] = mapped_column(String(30))
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    social_type: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone("Asia/Seoul", func.now()), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone("Asia/Seoul", func.now()), onupdate=func.timezone("Asia/Seoul", func.now()), nullable=False)

    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
