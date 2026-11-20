import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Memory, MemoryEmbedding, Persona, User
from app.services.embedding_service import generate_and_save_embedding
from app.services.memory_search import select_relevant_memories

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_automatic_embedding_generation_and_search():
    db = TestingSessionLocal()
    try:
        user = User(email="search_user@example.com", password_hash="hash")
        db.add(user)
        db.commit()

        persona = Persona(owner_id=user.id, name="Dada Jan")
        db.add(persona)
        db.commit()

        m1 = Memory(
            persona_id=persona.id,
            category="childhood",
            title="First bicycle",
            content="I bought you your first red bicycle when you were ten years old.",
            status="approved",
        )
        db.add(m1)
        db.commit()
        generate_and_save_embedding(db, m1)

        m2 = Memory(
            persona_id=persona.id,
            category="advice",
            title="Honesty",
            content="Always speak the truth, no matter how difficult it is.",
            status="approved",
        )
        db.add(m2)
        db.commit()
        generate_and_save_embedding(db, m2)

        # Verify embedding was created
        emb1 = db.scalars(
            select(MemoryEmbedding).where(MemoryEmbedding.memory_id == m1.id)
        ).first()
        assert emb1 is not None
        assert emb1.dimension == 384

        # Test semantic search retrieval
        memories = [m2, m1]  # unsorted / newest first
        relevant = select_relevant_memories(memories, "bicycle", limit=1, db=db)
        assert len(relevant) == 1
        assert relevant[0].id == m1.id
    finally:
        db.close()
