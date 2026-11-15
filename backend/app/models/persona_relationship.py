import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PersonaRelationship(Base):
    __tablename__ = "persona_relationships"

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    persona_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("personas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_name: Mapped[str] = mapped_column(String(150), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    preferred_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    biographical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_user_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    verification_status: Mapped[str] = mapped_column(
        String(30), default="verified", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
