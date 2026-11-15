
import json
import re
import uuid
from pathlib import Path

import edge_tts
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from app.services.chat_service import generate_chat_answer as _generate_chat_answer
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.ai.factory import get_llm_provider, get_model_name
from app.config import settings
from app.database import get_db
from app.dependencies import (
    fetch_owned_persona,
    get_current_user,
    get_owned_memory,
    get_owned_persona,
    get_owned_relationship,
    get_owned_video,
)
from app.models import (
    Conversation,
    MediaAsset,
    Memory,
    Persona,
    PersonaRelationship,
    User,
    VideoTranscript,
)
from app.rate_limit import limiter
from app.routers import auth, videos
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    HealthResponse,
    MediaAssetResponse,
    MemoryCreate,
    MemoryResponse,
    MemoryStatus,
    MemoryUpdate,
    PersonaCreate,
    PersonaResponse,
    RelationshipCreate,
    RelationshipResponse,
    RelationshipUpdate,
    TTSRequest,
)
from app.security import utcnow
from app.services.chat_service import (
    generate_chat_answer as _generate_chat_answer,
)
from app.services.transcription import transcribe_video_audio


# --------------------------------------------------
# Paths and limits
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEO_UPLOAD_DIR = PROJECT_ROOT / "uploads" / "videos"
AUDIO_UPLOAD_DIR = PROJECT_ROOT / "uploads" / "audio"

MAX_VIDEO_SIZE = settings.max_upload_mb * 1024 * 1024

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
}


class VoiceChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    persona_id: str | None = None
    session_id: str | None = Field(default=None, max_length=100)
    voice: str = Field(default="en-US-AriaNeural", max_length=100)
    session_id: str | None = Field(default=None, max_length=100)


# --------------------------------------------------
# Application
# --------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend foundation for an AI digital legacy "
        "and talking portrait platform."
    ),
)
app.add_middleware(
    CORSMiddleware,
  allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # frontend ka address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(auth.router)
app.include_router(videos.router)


# --------------------------------------------------
# System APIs
# --------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Digital Legacy API is running",
        "docs": "/docs",
    }


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["System"],
)
async def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception as exc:
        print(
            f"Database health check failed: "
            f"{type(exc).__name__}"
        )
        database_status = "unavailable"

    return HealthResponse(
        status=(
            "ok"
            if database_status == "connected"
            else "degraded"
        ),
        app_name=settings.app_name,
        version=settings.app_version,
        database=database_status,
        ai_provider=settings.ai_provider,
    )


# --------------------------------------------------
# Persona APIs
# --------------------------------------------------

@app.post(
    "/api/v1/personas",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Personas"],
)
def create_persona(
    payload: PersonaCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    persona = Persona(
        **payload.model_dump(),
        owner_id=user.id,
    )

    try:
        db.add(persona)
        db.commit()
        db.refresh(persona)
        return persona
    except Exception as exc:
        db.rollback()
        print(
            f"Persona creation failed: {type(exc).__name__}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create persona.",
        ) from exc


@app.get(
    "/api/v1/personas",
    response_model=list[PersonaResponse],
    tags=["Personas"],
)
def list_personas(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = (
        select(Persona)
        .where(Persona.owner_id == user.id)
        .order_by(Persona.created_at.desc())
    )
    return db.scalars(statement).all()


@app.get(
    "/api/v1/personas/{persona_id}",
    response_model=PersonaResponse,
    tags=["Personas"],
)
def get_persona(
    persona: Persona = Depends(get_owned_persona),
):
    return persona


# --------------------------------------------------
# Relationship APIs
# --------------------------------------------------

@app.post(
    "/api/v1/personas/{persona_id}/relationships",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Relationships"],
)
def create_relationship(
    payload: RelationshipCreate,
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    rel = PersonaRelationship(
        persona_id=persona.id,
        **payload.model_dump(),
    )
    try:
        db.add(rel)
        db.commit()
        db.refresh(rel)
        return rel
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create relationship.",
        ) from exc


@app.get(
    "/api/v1/personas/{persona_id}/relationships",
    response_model=list[RelationshipResponse],
    tags=["Relationships"],
)
def list_relationships(
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    statement = (
        select(PersonaRelationship)
        .where(PersonaRelationship.persona_id == persona.id)
        .order_by(PersonaRelationship.created_at.desc())
    )
    return db.scalars(statement).all()


@app.get(
    "/api/v1/relationships/{relationship_id}",
    response_model=RelationshipResponse,
    tags=["Relationships"],
)
def get_relationship(
    relationship: PersonaRelationship = Depends(get_owned_relationship),
):
    return relationship


@app.patch(
    "/api/v1/relationships/{relationship_id}",
    response_model=RelationshipResponse,
    tags=["Relationships"],
)
def update_relationship(
    payload: RelationshipUpdate,
    relationship: PersonaRelationship = Depends(get_owned_relationship),
    db: Session = Depends(get_db),
):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Nothing to update.")
    for field, value in changes.items():
        setattr(relationship, field, value)
    try:
        db.commit()
        db.refresh(relationship)
        return relationship
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update relationship.",
        ) from exc


@app.delete(
    "/api/v1/relationships/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Relationships"],
)
def delete_relationship(
    relationship: PersonaRelationship = Depends(get_owned_relationship),
    db: Session = Depends(get_db),
):
    try:
        db.delete(relationship)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete relationship.",
        ) from exc


# --------------------------------------------------
# Memory APIs
# --------------------------------------------------

def _save_memory(db: Session, memory: Memory) -> Memory:
    try:
        db.commit()
        db.refresh(memory)
        return memory
    except Exception as exc:
        db.rollback()
        print(
            f"Memory update failed: {type(exc).__name__}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update memory.",
        ) from exc


@app.post(
    "/api/v1/personas/{persona_id}/memories",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Memories"],
)
def create_memory(
    payload: MemoryCreate,
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    memory = Memory(
        persona_id=persona.id,
        category=payload.category,
        title=payload.title,
        content=payload.content,
        source="manual",
        confidence=None,
        verified=True,
        status="approved",
        reviewed_at=utcnow(),
    )

    try:
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory
    except Exception as exc:
        db.rollback()
        print(
            f"Memory creation failed: {type(exc).__name__}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save memory.",
        ) from exc


@app.get(
    "/api/v1/personas/{persona_id}/memories",
    response_model=list[MemoryResponse],
    tags=["Memories"],
)
def list_memories(
    status_filter: MemoryStatus | None = Query(
        default=None,
        alias="status",
    ),
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    statement = select(Memory).where(
        Memory.persona_id == persona.id
    )

    if status_filter:
        statement = statement.where(
            Memory.status == status_filter
        )

    return db.scalars(
        statement.order_by(Memory.created_at.desc())
    ).all()


@app.patch(
    "/api/v1/memories/{memory_id}",
    response_model=MemoryResponse,
    tags=["Memories"],
)
def edit_memory(
    payload: MemoryUpdate,
    memory: Memory = Depends(get_owned_memory),
    db: Session = Depends(get_db),
):
    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="Nothing to update.",
        )

    if (
        "content" in changes
        and changes["content"] is None
    ):
        raise HTTPException(
            status_code=422,
            detail="Content cannot be null.",
        )

    if (
        "category" in changes
        and changes["category"] is None
    ):
        raise HTTPException(
            status_code=422,
            detail="Category cannot be null.",
        )

    # Preserve the original content on the first content edit.
    if (
        "content" in changes
        and memory.original_content is None
        and changes["content"] != memory.content
    ):
        memory.original_content = memory.content

    for field, value in changes.items():
        setattr(memory, field, value)

    return _save_memory(db, memory)


@app.post(
    "/api/v1/memories/{memory_id}/approve",
    response_model=MemoryResponse,
    tags=["Memories"],
)
def approve_memory(
    memory: Memory = Depends(get_owned_memory),
    db: Session = Depends(get_db),
):
    memory.status = "approved"
    memory.verified = True
    memory.reviewed_at = utcnow()

    return _save_memory(db, memory)


@app.post(
    "/api/v1/memories/{memory_id}/reject",
    response_model=MemoryResponse,
    tags=["Memories"],
)
def reject_memory(
    memory: Memory = Depends(get_owned_memory),
    db: Session = Depends(get_db),
):
    memory.status = "rejected"
    memory.verified = False
    memory.reviewed_at = utcnow()

    return _save_memory(db, memory)


# --------------------------------------------------
# Conversation history
# --------------------------------------------------

@app.get(
    "/api/v1/personas/{persona_id}/conversations",
    response_model=list[ConversationResponse],
    tags=["Conversations"],
)
def list_conversations(
    limit: int = 50,
    offset: int = 0,
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="Limit must be between 1 and 100.",
        )

    if offset < 0:
        raise HTTPException(
            status_code=422,
            detail="Offset cannot be negative.",
        )

    statement = (
        select(Conversation)
        .where(Conversation.persona_id == persona.id)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


# --------------------------------------------------
# Chat APIs
# --------------------------------------------------

@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    tags=["AI"],
)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await _generate_chat_answer(
        payload,
        db,
        user,
    )


# --------------------------------------------------
# Video APIs
# --------------------------------------------------

@app.post(
    "/api/v1/personas/{persona_id}/video",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Videos"],
)
@limiter.limit("10/minute")
async def upload_persona_video(
    request: Request,
    file: UploadFile = File(...),
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    original_filename = (
        (file.filename or "video")
        .replace("\\", "/")
        .split("/")[-1]
    )
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported video format. "
                "Use MP4, MOV, AVI, MKV, or WEBM."
            ),
        )

    content_type = (
        file.content_type or "application/octet-stream"
    )

    if not (
        content_type.startswith("video/")
        or content_type == "application/octet-stream"
    ):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must be a video.",
        )

    VIDEO_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_filename = f"{uuid.uuid4()}{extension}"
    destination = VIDEO_UPLOAD_DIR / saved_filename
    size_bytes = 0

    try:
        with destination.open("wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                size_bytes += len(chunk)

                if size_bytes > MAX_VIDEO_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"Video exceeds the "
                            f"{settings.max_upload_mb} MB "
                            "upload limit."
                        ),
                    )

                output_file.write(chunk)

        if size_bytes == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded video is empty.",
            )

        # Basic file-signature validation.
        with destination.open("rb") as check_file:
            header = check_file.read(16)

        looks_like_video = (
            header[4:8] == b"ftyp"
            or header[:4] == b"\x1a\x45\xdf\xa3"
            or (
                header[:4] == b"RIFF"
                and header[8:12] == b"AVI "
            )
        )

        if not looks_like_video:
            raise HTTPException(
                status_code=400,
                detail="File content is not a valid video.",
            )

        asset = MediaAsset(
            persona_id=persona.id,
            original_filename=original_filename[:255],
            stored_path=f"uploads/videos/{saved_filename}",
            content_type=content_type,
            size_bytes=size_bytes,
            status="uploaded",
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    except Exception:
        db.rollback()

        if destination.exists():
            destination.unlink()

        raise

    finally:
        await file.close()


@app.get(
    "/api/v1/personas/{persona_id}/videos",
    response_model=list[MediaAssetResponse],
    tags=["Videos"],
)
def list_persona_videos(
    persona: Persona = Depends(get_owned_persona),
    db: Session = Depends(get_db),
):
    statement = (
        select(MediaAsset)
        .where(MediaAsset.persona_id == persona.id)
        .order_by(MediaAsset.created_at.desc())
    )

    return list(db.scalars(statement).all())


# --------------------------------------------------
# TTS and Voice Chat
# --------------------------------------------------

def _user_audio_dir(user: User) -> Path:
    directory = AUDIO_UPLOAD_DIR / user.id
    directory.mkdir(parents=True, exist_ok=True)
    return directory


@app.post(
    "/api/v1/tts/speak",
    tags=["TTS"],
)
@limiter.limit("10/minute")
async def generate_speech(
    request: Request,
    payload: TTSRequest,
    user: User = Depends(get_current_user),
):
    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = _user_audio_dir(user) / audio_filename

    try:
        communicate = edge_tts.Communicate(
            text=payload.text,
            voice=payload.voice,
        )
        await communicate.save(str(audio_path))

        if (
            not audio_path.exists()
            or audio_path.stat().st_size == 0
        ):
            raise RuntimeError(
                "TTS returned an empty audio file."
            )

        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=audio_filename,
        )

    except Exception as exc:
        if audio_path.exists():
            audio_path.unlink()

        print(f"TTS error: {type(exc).__name__}")

        raise HTTPException(
            status_code=502,
            detail=(
                "Speech generation failed. "
                "Check backend logs."
            ),
        ) from exc


@app.post(
    "/api/v1/chat/voice",
    tags=["AI"],
)
@limiter.limit("10/minute")
async def voice_chat(
    request: Request,
    payload: VoiceChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Reuse the shared chat service, including session support.
    chat_result = await _generate_chat_answer(
           ChatRequest(
               message=payload.message,
               persona_id=payload.persona_id,
               session_id=payload.session_id,
           ),
           db,
           user,
       )

    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = _user_audio_dir(user) / audio_filename

    try:
        communicate = edge_tts.Communicate(
            text=chat_result.answer,
            voice=payload.voice,
        )
        await communicate.save(str(audio_path))

        if (
            not audio_path.exists()
            or audio_path.stat().st_size == 0
        ):
            raise RuntimeError(
                "Generated audio is empty."
            )

        return {
            "answer": chat_result.answer,
            "provider": chat_result.provider,
            "model": chat_result.model,
            "session_id": chat_result.session_id,
            "audio_url": f"/api/v1/tts/audio/{audio_filename}",
        }

    except Exception as exc:
        if audio_path.exists():
            audio_path.unlink()

        print(
            f"Voice chat error: {type(exc).__name__}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Voice generation failed. "
                "Check backend logs."
            ),
        ) from exc


@app.get(
    "/api/v1/tts/audio/{filename}",
    tags=["TTS"],
)
def get_generated_audio(
    filename: str,
    user: User = Depends(get_current_user),
):
    # Only UUID-based MP3 filenames are allowed.
    try:
        if not filename.endswith(".mp3"):
            raise ValueError

        uuid.UUID(filename.removesuffix(".mp3"))

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid audio filename.",
        )

    # Audio files are isolated by authenticated user.
    audio_path = AUDIO_UPLOAD_DIR / user.id / filename

    if not audio_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Audio file not found.",
        )

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=filename,
    )
