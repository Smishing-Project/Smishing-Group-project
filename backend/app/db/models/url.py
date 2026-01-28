from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.db.database import Base


class Url(Base):
    __tablename__ = "urls"

    urls_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    msg_id: Mapped[int] = mapped_column(Integer, ForeignKey("messages.msg_id"), nullable=False)
    url_domain: Mapped[str] = mapped_column(Text, nullable=False)
    safe_browsing_result: Mapped[Optional[str]] = mapped_column(Text)
    ml_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    
    message: Mapped["Message"] = relationship(back_populates="urls")
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(back_populates="url")
