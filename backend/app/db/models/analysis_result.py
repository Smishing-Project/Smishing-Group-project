from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.db.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_result"

    analysis_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    msg_id: Mapped[int] = mapped_column(Integer, ForeignKey("messages.msg_id"), nullable=False)
    urls_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("urls.urls_id"))
    smishing_type: Mapped[Optional[str]] = mapped_column(String(30))
    risk_score: Mapped[Optional[float]] = mapped_column(Float)
    keywords: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone("Asia/Seoul", func.now()), nullable=False)
    
    message: Mapped["Message"] = relationship(back_populates="analysis_results")
    url: Mapped[Optional["Url"]] = relationship(back_populates="analysis_results")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="analysis_result", cascade="all, delete-orphan")
