from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    notifi_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(Integer, ForeignKey("analysis_result.analysis_id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="sms")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone("Asia/Seoul", func.now()), nullable=False)
    
    analysis_result: Mapped["AnalysisResult"] = relationship(back_populates="notifications")
    user: Mapped["User"] = relationship(back_populates="notifications")
