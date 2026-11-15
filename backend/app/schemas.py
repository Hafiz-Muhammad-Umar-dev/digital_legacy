from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    database: str
    ai_provider: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    persona_id: str | None = None
    session_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    provider: str
    model: str
    session_id: str | None = None


class PersonaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    biography: str | None = None
    personality_traits: str | None = None
    speaking_style: str | None = None
    preferred_language: str = Field(default="English", max_length=30)


class PersonaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    biography: str | None
    personality_traits: str | None
    speaking_style: str | None
    preferred_language: str
    portrait_path: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class RelationshipCreate(BaseModel):
    member_name: str = Field(min_length=1, max_length=150)
    relationship_type: str = Field(min_length=1, max_length=80)
    preferred_name: str | None = Field(default=None, max_length=150)
    biographical_notes: str | None = Field(default=None, max_length=5000)
    linked_user_id: str | None = Field(default=None, max_length=36)
    verification_status: str = Field(default="verified", max_length=30)


class RelationshipUpdate(BaseModel):
    member_name: str | None = Field(default=None, min_length=1, max_length=150)
    relationship_type: str | None = Field(default=None, min_length=1, max_length=80)
    preferred_name: str | None = Field(default=None, max_length=150)
    biographical_notes: str | None = Field(default=None, max_length=5000)
    linked_user_id: str | None = Field(default=None, max_length=36)
    verification_status: str | None = Field(default=None, max_length=30)


class RelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    persona_id: str
    member_name: str
    relationship_type: str
    preferred_name: str | None
    biographical_notes: str | None
    linked_user_id: str | None
    verification_status: str
    created_at: datetime
    updated_at: datetime


MemoryStatus = Literal["pending_review", "approved", "rejected"]


class MemoryCreate(BaseModel):
    category: str = Field(default="general", min_length=1, max_length=80)
    title: str | None = Field(default=None, max_length=200)
    content: str = Field(min_length=1, max_length=10000)


class MemoryUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=80)
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=10000)


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    persona_id: str
    category: str
    title: str | None
    content: str
    source: str
    confidence: float | None
    verified: bool
    status: MemoryStatus
    original_content: str | None
    reviewed_at: datetime | None
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    persona_id: str
    session_id: str | None
    user_message: str
    assistant_response: str
    created_at: datetime


class MediaAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    persona_id: str
    original_filename: str
    stored_path: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    voice: str = Field(
        default="en-US-AriaNeural",
        min_length=1,
        max_length=100,
    )
