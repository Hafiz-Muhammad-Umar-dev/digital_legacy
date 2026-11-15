import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Persona
from app.services.chat_service import _persona_prompt

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def register_and_login(email=None, password="password123"):
    if not email:
        email = f"user_{uuid.uuid4()}@example.com"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]


def test_1_create_relationship():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    p_res = client.post(
        "/api/v1/personas",
        json={"name": "Dada Jan", "biography": "Loving grandfather."},
        headers=headers,
    )
    assert p_res.status_code == 201
    persona_id = p_res.json()["id"]

    rel_res = client.post(
        f"/api/v1/personas/{persona_id}/relationships",
        json={
            "member_name": "Muhammad Umar",
            "relationship_type": "Grandson",
            "preferred_name": "Umar",
            "biographical_notes": "Son of Ahmed",
        },
        headers=headers,
    )
    assert rel_res.status_code == 201
    data = rel_res.json()
    assert data["member_name"] == "Muhammad Umar"
    assert data["relationship_type"] == "Grandson"
    assert data["preferred_name"] == "Umar"


def test_2_retrieve_and_update_relationship():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    p_res = client.post(
        "/api/v1/personas",
        json={"name": "Dada Jan"},
        headers=headers,
    )
    persona_id = p_res.json()["id"]

    rel_res = client.post(
        f"/api/v1/personas/{persona_id}/relationships",
        json={
            "member_name": "Umar",
            "relationship_type": "Grandson",
        },
        headers=headers,
    )
    rel_id = rel_res.json()["id"]

    # Update relationship
    patch_res = client.patch(
        f"/api/v1/relationships/{rel_id}",
        json={"preferred_name": "Umar Bhai"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["preferred_name"] == "Umar Bhai"

    # Delete relationship
    del_res = client.delete(
        f"/api/v1/relationships/{rel_id}",
        headers=headers,
    )
    assert del_res.status_code == 204


def test_7_unauthorized_access():
    token1 = register_and_login()
    token2 = register_and_login()

    p_res = client.post(
        "/api/v1/personas",
        json={"name": "Dada Jan"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    persona_id = p_res.json()["id"]

    rel_res = client.post(
        f"/api/v1/personas/{persona_id}/relationships",
        json={"member_name": "Umar", "relationship_type": "Grandson"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    rel_id = rel_res.json()["id"]

    get_res = client.get(
        f"/api/v1/relationships/{rel_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert get_res.status_code == 404


def test_8_and_9_chat_and_unconfigured_persona():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    p_res = client.post(
        "/api/v1/personas",
        json={"name": "Old Friend"},
        headers=headers,
    )
    persona_id = p_res.json()["id"]

    old_provider = settings.ai_provider
    settings.ai_provider = "mock"
    try:
        chat_res = client.post(
            "/api/v1/chat",
            json={"message": "Hello", "persona_id": persona_id},
            headers=headers,
        )
        assert chat_res.status_code == 200
        assert "answer" in chat_res.json()
    finally:
        settings.ai_provider = old_provider


def test_10_prompt_inspection_includes_relationships():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    p_res = client.post(
        "/api/v1/personas",
        json={"name": "Dada Jan", "biography": "Family patriarch."},
        headers=headers,
    )
    persona_id = p_res.json()["id"]

    client.post(
        f"/api/v1/personas/{persona_id}/relationships",
        json={
            "member_name": "Muhammad Umar",
            "relationship_type": "Grandson",
            "preferred_name": "Umar",
            "biographical_notes": "Son of Ahmed, engineer",
        },
        headers=headers,
    )

    db = TestingSessionLocal()
    try:
        persona = db.get(Persona, persona_id)
        prompt = _persona_prompt(db, persona, "Hello Dada")
        assert "KNOWN FAMILY RELATIONSHIPS" in prompt
        assert "Muhammad Umar" in prompt
        assert "Grandson" in prompt
        assert "Umar" in prompt
        assert "Son of Ahmed, engineer" in prompt
    finally:
        db.close()


def test_11_greeting_recognition_chat():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    p_res = client.post(
        "/api/v1/personas",
        json={"name": "Dada Jan"},
        headers=headers,
    )
    persona_id = p_res.json()["id"]

    client.post(
        f"/api/v1/personas/{persona_id}/relationships",
        json={
            "member_name": "Muhammad Umar",
            "relationship_type": "Grandson",
            "preferred_name": "Umar",
        },
        headers=headers,
    )

    old_provider = settings.ai_provider
    settings.ai_provider = "mock"
    try:
        chat_res = client.post(
            "/api/v1/chat",
            json={"message": "Hello Dada, I am your grandson Umar.", "persona_id": persona_id},
            headers=headers,
        )
        assert chat_res.status_code == 200
        data = chat_res.json()
        assert "answer" in data
        assert data["provider"] == "mock"
    finally:
        settings.ai_provider = old_provider
