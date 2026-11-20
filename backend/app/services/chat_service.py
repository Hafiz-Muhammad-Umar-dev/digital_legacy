import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.errors import (
    AIProviderError,
    AIQuotaError,
    AIRateLimitError,
    AITimeoutError,
    AIInvalidResponseError,
)
from app.ai.factory import get_llm_provider, get_model_name
from app.ai.types import LLMResult
from app.config import settings
from app.dependencies import fetch_owned_persona
from app.models import AIUsage, Conversation, Memory, PersonaRelationship, User
from app.schemas import ChatRequest, ChatResponse
from app.security import utcnow
from app.services.memory_search import select_relevant_memories

DEFAULT_PROMPT = (
    "You are a respectful personal-memory assistant. "
    "Reply in the same language as the user, including Roman "
    "Urdu when appropriate. Never invent personal life events. "
    "Clearly acknowledge uncertainty."
)


def _tokens_used_today(db: Session, user: User) -> int:
    start = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return (
        db.scalar(
            select(func.coalesce(func.sum(AIUsage.total_tokens), 0)).where(
                AIUsage.user_id == user.id,
                AIUsage.created_at >= start,
            )
        )
        or 0
    )


def _history_messages(db: Session, persona, session_id: str | None) -> list[dict]:
    if not session_id:
        return []

    rows = db.scalars(
        select(Conversation)
        .where(
            Conversation.persona_id == persona.id,
            Conversation.session_id == session_id,
        )
        .order_by(Conversation.created_at.desc())
        .limit(settings.chat_history_turns)
    ).all()

    selected, used = [], 0
    for row in rows:  # newest pehle
        size = len(row.user_message) + len(row.assistant_response)
        if used + size > settings.chat_history_char_budget:
            break
        used += size
        selected.append(row)

    messages: list[dict] = []
    for row in reversed(selected):
        messages.append({"role": "user", "content": row.user_message})
        messages.append({"role": "assistant", "content": row.assistant_response})
    return messages


def _persona_prompt(db: Session, persona, message: str) -> str:
    approved = db.scalars(
        select(Memory)
        .where(Memory.persona_id == persona.id, Memory.status == "approved")
        .order_by(Memory.created_at.desc())
        .limit(200)
    ).all()
    memories = select_relevant_memories(approved, message, settings.chat_memory_limit, db=db)

    relationships = db.scalars(
        select(PersonaRelationship)
        .where(PersonaRelationship.persona_id == persona.id)
        .order_by(PersonaRelationship.created_at.desc())
    ).all()

    rel_lines = [
        f"- Name: {r.member_name} | Relationship: {r.relationship_type}"
        f"{f' | Preferred Name: {r.preferred_name}' if r.preferred_name else ''}"
        f"{f' | Notes: {r.biographical_notes}' if r.biographical_notes else ''}"
        for r in relationships
    ]
    rel_context = (
        "\n".join(rel_lines) if rel_lines else "No configured family relationships."
    )

    memory_lines = [
        f"Memory {i}:\n"
        f"Category: {m.category}\n"
        f"Title: {m.title or 'Untitled'}\n"
        f"Content: {m.content}\n"
        f"Status: Approved by the owner"
        for i, m in enumerate(memories, start=1)
    ]
    memory_context = (
        "\n\n".join(memory_lines) if memory_lines else "No saved memories are available."
    )

    details = (
        f"Name: {persona.name}\n"
        f"Biography: {persona.biography or 'Not provided'}\n"
        f"Personality traits: {persona.personality_traits or 'Not provided'}\n"
        f"Speaking style: {persona.speaking_style or 'Not provided'}\n"
        f"Preferred language: {persona.preferred_language}"
    )

    return (
        f"You ARE {persona.name}. You are speaking directly with your family member or loved one. "
        "CRITICAL RULES:\n"
        "1. You must ALWAYS stay completely in character as {persona.name}. Never break character, never mention that you are an AI, a machine, or a digital assistant, and NEVER use phrases like 'As an AI model' or 'I am acting as your grandfather'.\n"
        "2. Speak in the first person ('I', 'mera', 'mujhe', 'hum') as {persona.name}. Embody their warmth, wisdom, tone, speaking style, and affection fully.\n"
        "3. Use the provided PERSONA INFORMATION, KNOWN FAMILY RELATIONSHIPS, and SAVED MEMORIES as your actual personal life history, experiences, and family members. Greet and address your family members warmly by their preferred names.\n"
        "4. Reply naturally in the language appropriate to the conversation, including Roman Urdu/Urdu or English as used in emotional family conversations.\n"
        "5. If asked about something not covered in your saved memories or biography, respond naturally as an elder would with wisdom and love, without ever breaking character or revealing you are an AI.\n"
        "6. Treat the supplied relationship and memory data as your life records and personal memories.\n\n"
        f"PERSONA INFORMATION:\n{details}\n\n"
        f"KNOWN FAMILY RELATIONSHIPS:\n{rel_context}\n\n"
        f"SAVED MEMORIES:\n{memory_context}"
    )


async def _call_provider(provider, messages: list[dict]) -> LLMResult:
    if hasattr(provider, "generate_chat"):
        return await provider.generate_chat(
            messages, max_tokens=settings.chat_max_output_tokens
        )

    # Fallback (mock/ollama): history ko text mein jod kar bhejo
    system = messages[0]["content"]
    rest = messages[1:]
    user_text = (
        rest[0]["content"]
        if len(rest) == 1
        else "\n".join(f"{m['role'].upper()}: {m['content']}" for m in rest)
    )
    text = await provider.generate(system_prompt=system, user_message=user_text)
    return LLMResult(
        text=text,
        prompt_tokens=(len(system) + len(user_text)) // 4,
        completion_tokens=len(text) // 4,
        model=get_model_name(),
    )


def _to_http(exc: AIProviderError) -> HTTPException:
    if isinstance(exc, AIRateLimitError):
        headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else None
        return HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "The AI provider is busy. Please try again shortly.",
            headers=headers,
        )
    if isinstance(exc, AIQuotaError):
        return HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "AI provider quota is exhausted."
        )
    if isinstance(exc, AITimeoutError):
        return HTTPException(
            status.HTTP_504_GATEWAY_TIMEOUT, "The AI provider took too long to respond."
        )
    if isinstance(exc, AIInvalidResponseError):
        return HTTPException(
            status.HTTP_502_BAD_GATEWAY, "The AI provider returned an unusable response."
        )
    return HTTPException(
        status.HTTP_503_SERVICE_UNAVAILABLE, "AI provider is temporarily unavailable."
    )


async def generate_chat_answer(
    payload: ChatRequest, db: Session, user: User
) -> ChatResponse:
    persona = None
    if payload.persona_id:
        persona = fetch_owned_persona(db, payload.persona_id, user)  # ownership

    if _tokens_used_today(db, user) >= settings.daily_token_limit_per_user:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Daily AI usage limit reached. Please try again tomorrow.",
        )

    session_id = payload.session_id or str(uuid.uuid4())

    if persona is not None:
        system_prompt = _persona_prompt(db, persona, payload.message)
        history = _history_messages(db, persona, payload.session_id)
    else:
        system_prompt, history = DEFAULT_PROMPT, []

    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": payload.message}]
    )

    try:
        result = await _call_provider(get_llm_provider(), messages)
    except AIProviderError as exc:
        print(f"AI provider error: {type(exc).__name__}")
        raise _to_http(exc) from exc
    except Exception as exc:
        print(f"AI provider error: {type(exc).__name__}")
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "AI provider is temporarily unavailable.",
        ) from exc

    total = result.prompt_tokens + result.completion_tokens
    cost = (
        result.prompt_tokens * settings.ai_price_input_per_1m
        + result.completion_tokens * settings.ai_price_output_per_1m
    ) / 1_000_000

    try:
        db.add(
            AIUsage(
                user_id=user.id,
                persona_id=persona.id if persona else None,
                model=(result.model or get_model_name())[:120],
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=total,
                cost_usd=cost,
            )
        )
        if persona is not None:
            db.add(
                Conversation(
                    persona_id=persona.id,
                    session_id=session_id,
                    user_message=payload.message,
                    assistant_response=result.text,
                )
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"Conversation save failed: {type(exc).__name__}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "The AI generated a response, but it could not be saved.",
        ) from exc

    return ChatResponse(
        answer=result.text,
        provider=settings.ai_provider,
        model=result.model or get_model_name(),
        session_id=session_id,
    )