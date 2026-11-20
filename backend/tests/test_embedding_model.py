import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Memory, MemoryEmbedding, Persona, User

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


def test_memory_embedding_model_instantiation():
    db = TestingSessionLocal()
    try:
        # Create user, persona, and memory
        user = User(email="emb_user@example.com", password_hash="hash")
        db.add(user)
        db.commit()

        persona = Persona(owner_id=user.id, name="Test Persona")
        db.add(persona)
        db.commit()

        memory = Memory(
            persona_id=persona.id,
            category="general",
            content="Test memory content for embedding.",
            status="approved",
        )
        db.add(memory)
        db.commit()

        # Create embedding record
        embedding = MemoryEmbedding(
            memory_id=memory.id,
            embedding_json="[0.1, 0.2, 0.3]",
            dimension=3,
            model_name="all-MiniLM-L6-v2",
        )
        db.add(embedding)
        db.commit()

        fetched = db.get(MemoryEmbedding, embedding.id)
        assert fetched is not None
        assert fetched.memory_id == memory.id
        assert fetched.dimension == 3
        assert fetched.model_name == "all-MiniLM-L6-v2"
        assert fetched.embedding_json == "[0.1, 0.2, 0.3]"
        assert fetched.created_at is not None
        assert fetched.updated_at is not None
    finally:
        db.close()


def test_memory_embedding_unique_constraint():
    db = TestingSessionLocal()
    try:
        user = User(email="emb_unique@example.com", password_hash="hash")
        db.add(user)
        db.commit()

        persona = Persona(owner_id=user.id, name="Persona Unique")
        db.add(persona)
        db.commit()

        memory = Memory(
            persona_id=persona.id,
            content="Unique memory content.",
            status="approved",
        )
        db.add(memory)
        db.commit()

        emb1 = MemoryEmbedding(
            memory_id=memory.id,
            embedding_json="[0.1]",
            dimension=1,
            model_name="test-model",
        )
        db.add(emb1)
        db.commit()

        # Attempting duplicate embedding for same memory_id should fail (unique constraint)
        emb2 = MemoryEmbedding(
            memory_id=memory.id,
            embedding_json="[0.2]",
            dimension=1,
            model_name="test-model",
        )
        db.add(emb2)
        with pytest.raises(Exception):
            db.commit()
    finally:
        db.rollback()
        db.close()
