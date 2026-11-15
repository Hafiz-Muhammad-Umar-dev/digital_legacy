from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_owned_video
from app.models import MediaAsset, ProcessingJob
from app.rate_limit import limiter

router = APIRouter(prefix="/api/v1/videos", tags=["Videos"])


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_asset_id: str
    status: str
    stage: str | None
    attempts: int
    max_attempts: int
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


def _active_job(db: Session, asset_id: str) -> ProcessingJob | None:
    return db.scalar(
        select(ProcessingJob).where(ProcessingJob.active_key == asset_id)
    )


@router.post(
    "/{video_id}/process",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit("10/minute")
def start_processing(
    request: Request,
    asset: MediaAsset = Depends(get_owned_video),
    db: Session = Depends(get_db),
):
    if asset.status == "processed":
        raise HTTPException(409, "This video has already been processed.")

    active = _active_job(db, asset.id)
    if active is not None:
        return active  # duplicate job nahi banta

    job = ProcessingJob(media_asset_id=asset.id, active_key=asset.id)
    try:
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except IntegrityError:
        # Race condition: do requests ek saath aayin, UNIQUE ne rok liya
        db.rollback()
        active = _active_job(db, asset.id)
        if active is not None:
            return active
        raise HTTPException(500, "Could not create processing job.")


@router.get("/{video_id}/job", response_model=JobResponse)
def get_latest_job(
    asset: MediaAsset = Depends(get_owned_video),
    db: Session = Depends(get_db),
):
    job = db.scalar(
        select(ProcessingJob)
        .where(ProcessingJob.media_asset_id == asset.id)
        .order_by(ProcessingJob.created_at.desc())
        .limit(1)
    )
    if job is None:
        raise HTTPException(404, "No processing job for this video.")
    return job