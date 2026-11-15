
from datetime import datetime

from sqlalchemy import (
    DateTime, Float, ForeignKey, Index, String, Text, func
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    persona_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("personas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(80), default="general", nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(
        String(80), default="user_provided", nullable=False
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    verified: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    status: Mapped[str] = mapped_column(
    String(20),
    default="pending_review",
    server_default="pending_review",
    nullable=False,
    )
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_memories_persona_status", "persona_id", "status"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
