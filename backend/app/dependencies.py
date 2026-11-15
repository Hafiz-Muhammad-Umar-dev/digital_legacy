from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.models.persona_relationship import PersonaRelationship
from app.database import get_db
from app.models.media_asset import MediaAsset
from app.models.persona import Persona
from app.models.user import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def fetch_owned_persona(db: Session, persona_id: str, user: User) -> Persona:
    """Persona na ho ya kisi aur ki ho, dono case mein same 404 (existence leak nahi)."""
    persona = db.scalar(
        select(Persona).where(
            Persona.id == persona_id,
            Persona.owner_id == user.id,
        )
    )
    if persona is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Persona not found.")
    return persona


def get_owned_persona(
    persona_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Persona:
    return fetch_owned_persona(db, persona_id, user)


def get_owned_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaAsset:
    """video -> persona -> owner chain check."""
    asset = db.scalar(
        select(MediaAsset)
        .join(Persona, Persona.id == MediaAsset.persona_id)
        .where(MediaAsset.id == video_id, Persona.owner_id == user.id)
    )
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Video not found.")
    return asset

def get_owned_memory(
    memory_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Memory:
    """memory -> persona -> owner chain check."""
    memory = db.scalar(
        select(Memory)
        .join(Persona, Persona.id == Memory.persona_id)
        .where(Memory.id == memory_id, Persona.owner_id == user.id)
    )
    if memory is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Memory not found.")
    return memory


def get_owned_relationship(
    relationship_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonaRelationship:
    """relationship -> persona -> owner chain check."""
    rel = db.scalar(
        select(PersonaRelationship)
        .join(Persona, Persona.id == PersonaRelationship.persona_id)
        .where(PersonaRelationship.id == relationship_id, Persona.owner_id == user.id)
    )
    if rel is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Relationship not found.")
    return rel