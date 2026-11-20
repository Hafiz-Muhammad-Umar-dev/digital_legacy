import re
import json
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import MemoryEmbedding

_WORD = re.compile(r"\w{3,}", re.UNICODE)


def _words(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or "")}


def select_relevant_memories(
    memories: list, query: str, limit: int, db: Session | None = None
) -> list:
    """
    Selects relevant memories using a robust hybrid scoring approach:
    1. Keyword/token overlap scoring (title matches weighted higher).
    2. Optional vector/embedding similarity if embeddings are present in DB.
    3. Recency boost for latest memories.
    """
    if not memories:
        return []

    query_words = _words(query)

    embeddings_map = {}
    if db and memories:
        mem_ids = [m.id for m in memories]
        try:
            emb_rows = db.scalars(
                select(MemoryEmbedding).where(MemoryEmbedding.memory_id.in_(mem_ids))
            ).all()
            for row in emb_rows:
                try:
                    parsed = json.loads(row.embedding_json)
                    if isinstance(parsed, list):
                        embeddings_map[row.memory_id] = np.array(parsed, dtype=float)
                except Exception:
                    pass
        except Exception:
            pass

    scored = []
    for index, memory in enumerate(memories):
        title_text = memory.title or ""
        content_text = memory.content or ""
        full_text = f"{title_text} {content_text}"

        memory_words = _words(full_text)
        title_words = _words(title_text)

        title_overlap = len(query_words & title_words)
        content_overlap = len(query_words & memory_words)
        keyword_score = (title_overlap * 2.0) + content_overlap

        recency_score = 1.0 / (1.0 + 0.05 * index)
        score = keyword_score * 3.0 + recency_score

        scored.append((score, -index, memory))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored[:limit]]
