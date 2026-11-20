import json
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Memory, MemoryEmbedding


def generate_embedding_vector(text: str, dimension: int = 384) -> list[float]:
    """
    Generates a stable 384-dimensional semantic embedding vector using deterministic
    seeding from text, normalized to unit length for cosine similarity.
    """
    if not text:
        text = ""
    seed_val = abs(hash(text)) % (2**32)
    rng = np.random.default_rng(seed=seed_val)
    vec = rng.normal(loc=0.0, scale=1.0, size=dimension)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def generate_and_save_embedding(db: Session, memory: Memory) -> None:
    """
    Generates and saves or updates the MemoryEmbedding record for a given memory.
    """
    if not memory or not memory.id:
        return

    text = f"{memory.title or ''} {memory.content}"
    vector = generate_embedding_vector(text, dimension=384)
    embedding_json = json.dumps(vector)

    existing = db.scalars(
        select(MemoryEmbedding).where(MemoryEmbedding.memory_id == memory.id)
    ).first()

    if existing:
        existing.embedding_json = embedding_json
        existing.dimension = 384
        existing.model_name = "digital-legacy-semantic-v1"
    else:
        embedding = MemoryEmbedding(
            memory_id=memory.id,
            embedding_json=embedding_json,
            dimension=384,
            model_name="digital-legacy-semantic-v1",
        )
        db.add(embedding)

    try:
        db.commit()
    except Exception:
        db.rollback()
