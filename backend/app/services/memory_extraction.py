import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MediaAsset, Memory, VideoTranscript


class PermanentJobError(Exception):
    """Retry se theek nahi hoga (missing file, khali transcript)."""


EXTRACTION_PROMPT = """
You are a factual autobiographical memory extraction system.

Extract up to 5 useful personal facts from the transcript.

Rules:
- Use only facts explicitly supported by the transcript.
- Never invent names, dates, relationships, locations, or experiences.
- If speech recognition is unclear, omit the uncertain fact.
- Do not assume a person lives in a location merely because
  they mention that location.
- Do not include guesses or explanations.
- Return ONLY a valid JSON array.
- Do not use Markdown code fences.
- Do not include reasoning outside the JSON.
- If no reliable personal facts exist, return [].

Each item must have exactly these fields:
{
  "category": "general",
  "title": "Short title",
  "content": "A factual memory supported by the transcript.",
  "confidence": 0.8
}

Confidence must be a number between 0 and 1.
Return no more than 3 items.
Keep each content field to one short sentence.
Use concise titles.
Return the complete JSON array.
Do not start an item unless you can finish the entire response.
"""


def _parse_json_array(raw: str) -> list:
    raw = raw.strip()

    if raw.startswith("```"):
        raw = re.sub(r"\A```(?:json)?\s*", "", raw, count=1, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```\s*\Z", "", raw, count=1).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end < start:
            raise ValueError("AI did not return a JSON array.")
        try:
            data = json.loads(raw[start:end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("AI returned invalid JSON.") from exc

    if not isinstance(data, list):
        raise ValueError("AI response must be a JSON array.")
    return data


async def extract_memories(db: Session, asset: MediaAsset, provider) -> int:
    """Pending_review memories banata hai. Pehle se hon to 0 return (idempotent)."""
    record = db.get(VideoTranscript, asset.id)
    if record is None:
        raise PermanentJobError("Transcript is missing.")

    transcript = record.transcript
    if not isinstance(transcript, str) or not transcript.strip():
        raise PermanentJobError("The saved transcript is empty.")

    source = f"video_transcript:{asset.id}"

    existing = db.scalars(
        select(Memory).where(
            Memory.persona_id == asset.persona_id,
            Memory.source == source,
        )
    ).first()
    if existing is not None:
        return 0

    raw = await provider.generate(
        system_prompt=EXTRACTION_PROMPT,
        user_message=(
            "Extract factual autobiographical memories from this transcript.\n\n"
            "TRANSCRIPT:\n" + transcript[:6000]
        ),
    )
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("AI returned an empty response.")

    saved = 0
    for item in _parse_json_array(raw)[:5]:
        if not isinstance(item, dict):
            continue

        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            continue

        category = item.get("category", "general")
        title = item.get("title")
        if not isinstance(category, str):
            category = "general"
        if not isinstance(title, str):
            title = None

        try:
            confidence = float(item.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))

        db.add(
            Memory(
                persona_id=asset.persona_id,
                category=category.strip()[:80] or "general",
                title=title.strip()[:200] if title and title.strip() else None,
                content=content.strip(),
                source=source,
                confidence=confidence,
                verified=False,
                status="pending_review",
            )
        )
        saved += 1

    db.commit()
    return saved