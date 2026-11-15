
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base


class VideoTranscript(Base):
    __tablename__ = "video_transcripts"

    media_asset_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("media_assets.id", ondelete="CASCADE"),
        primary_key=True,
    )

    language: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    duration_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    transcript: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    segments: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
