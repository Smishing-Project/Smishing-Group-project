from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.db.database import Base


class Message(Base):
    __tablename__ = "messages"

    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)
    masked_text: Mapped[Optional[str]] = mapped_column(Text)
    extracted_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone("Asia/Seoul", func.now()), nullable=False)
    
    user: Mapped["User"] = relationship(back_populates="messages")
    urls: Mapped[list["Url"]] = relationship(back_populates="message", cascade="all, delete-orphan")
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(back_populates="message", cascade="all, delete-orphan")
