import asyncio
import time
from datetime import timedelta
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.ai.factory import get_llm_provider
from app.database import SessionLocal
from app.models import MediaAsset, ProcessingJob, VideoTranscript
from app.security import utcnow
from app.services.memory_extraction import PermanentJobError, extract_memories
from app.services.transcription import transcribe_video_audio

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POLL_SECONDS = 3
STALE_AFTER = timedelta(minutes=30)
RETRY_DELAYS = [30, 120, 300]  # seconds


def _mark_failure(job: ProcessingJob, message: str, retryable: bool) -> None:
    job.error = message[:500]
    if retryable and job.attempts < job.max_attempts:
        delay = RETRY_DELAYS[min(job.attempts - 1, len(RETRY_DELAYS) - 1)]
        job.status = "queued"
        job.next_run_at = utcnow() + timedelta(seconds=delay)
    else:
        job.status = "failed"
        job.finished_at = utcnow()
        job.active_key = None  # ab dobara process kiya ja sakta hai


def recover_stale_jobs(db: Session) -> None:
    cutoff = utcnow() - STALE_AFTER
    stale = db.scalars(
        select(ProcessingJob).where(
            ProcessingJob.status == "running",
            ProcessingJob.started_at < cutoff,
        )
    ).all()
    for job in stale:
        _mark_failure(job, "Worker stopped unexpectedly.", retryable=True)
    if stale:
        db.commit()
        print(f"Recovered {len(stale)} stale job(s)")


def claim_next_job(db: Session) -> str | None:
    now = utcnow()
    job_id = db.scalar(
        select(ProcessingJob.id)
        .where(ProcessingJob.status == "queued", ProcessingJob.next_run_at <= now)
        .order_by(ProcessingJob.created_at)
        .limit(1)
    )
    if job_id is None:
        return None

    # Atomic claim: sirf ek worker ko rowcount == 1 milega
    result = db.execute(
        update(ProcessingJob)
        .where(ProcessingJob.id == job_id, ProcessingJob.status == "queued")
        .values(
            status="running",
            started_at=now,
            attempts=ProcessingJob.attempts + 1,
            error=None,
        )
    )
    db.commit()
    return job_id if result.rowcount == 1 else None


def _transcribe_if_needed(db: Session, asset: MediaAsset) -> None:
    if db.get(VideoTranscript, asset.id) is not None:
        return  # pehle se transcribed

    video_path = PROJECT_ROOT / asset.stored_path
    if not video_path.exists():
        raise PermanentJobError("Video file is missing on the server.")

    result = transcribe_video_audio(str(video_path))
    db.add(
        VideoTranscript(
            media_asset_id=asset.id,
            language=result["language"],
            duration_seconds=result["duration_seconds"],
            transcript=result["transcript"],
            segments=result["segments"],
        )
    )
    asset.status = "transcribed"
    db.commit()


def process_job(job_id: str) -> None:
    db = SessionLocal()
    stage = "starting"
    try:
        job = db.get(ProcessingJob, job_id)
        asset = db.get(MediaAsset, job.media_asset_id)
        print(f"Job {job_id[:8]} started (attempt {job.attempts}/{job.max_attempts})")

        stage = "transcribing"
        job.stage = stage
        db.commit()
        _transcribe_if_needed(db, asset)

        stage = "extracting"
        job.stage = stage
        db.commit()
        asyncio.run(extract_memories(db, asset, get_llm_provider()))

        job.status = "succeeded"
        job.stage = "done"
        job.finished_at = utcnow()
        job.active_key = None
        asset.status = "processed"
        db.commit()
        print(f"Job {job_id[:8]} succeeded")

    except Exception as exc:
        db.rollback()
        permanent = isinstance(exc, PermanentJobError)
        safe = str(exc) if isinstance(exc, (PermanentJobError, ValueError)) else type(exc).__name__
        print(f"Job {job_id[:8]} failed at {stage}: {type(exc).__name__}")

        job = db.get(ProcessingJob, job_id)
        _mark_failure(job, f"{stage}: {safe}", retryable=not permanent)
        db.commit()
    finally:
        db.close()


def main() -> None:
    print("Worker started. Ctrl+C se band karo.")
    last_recovery = 0.0
    try:
        while True:
            job_id = None
            try:
                with SessionLocal() as db:
                    if time.monotonic() - last_recovery > 60:
                        recover_stale_jobs(db)
                        last_recovery = time.monotonic()
                    job_id = claim_next_job(db)
            except Exception as exc:
                print(f"Worker loop error: {type(exc).__name__}")

            if job_id:
                process_job(job_id)
            else:
                time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("Worker stopped.")


if __name__ == "__main__":
    main()