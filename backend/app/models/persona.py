
from datetime import datetime
from sqlalchemy import Column, CHAR, ForeignKey
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from app.database import Base


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    owner_id: Mapped[str | None] = mapped_column(
    CHAR(36),
    ForeignKey("users.id", ondelete="CASCADE"),
    index=True,
    nullable=True,  # purana data bachane ke liye abhi nullable
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality_traits: Mapped[str | None] = mapped_column(Text, nullable=True)
    speaking_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_language: Mapped[str] = mapped_column(
        String(30), default="English", nullable=False
    )
    portrait_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="draft", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
    owner_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    