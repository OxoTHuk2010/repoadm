from sqlalchemy import select, update
from sqlalchemy.orm import Session

from repoadm.models import (
    JobStatus,
    SyncJob,
)
from repoadm.utils import utcnow

def claim_next_job(
    db: Session,
) -> SyncJob | None:
    """
    Переводит самый старый QUEUED job
    в RUNNING и возвращает его.

    Если очередь пуста, возвращает None.
    """
    next_job_id = (
        select(SyncJob.id)
        .where(
            SyncJob.status == JobStatus.QUEUED
        )
        .order_by(
            SyncJob.created_at,
            SyncJob.id,
        )
        .limit(1)
        .scalar_subquery()
    )

    stmt = (
        update(SyncJob)
        .where(
            SyncJob.id == next_job_id,
            SyncJob.status == JobStatus.QUEUED,
        )
        .values(
            status = JobStatus.RUNNING,
            started_at = utcnow(),
        )
        .returning(SyncJob.id)
    )

    job_id = db.scalar(stmt)

    if job_id is None:
        db.rollback()
        return None

    db.commit()

    return db.get(
        SyncJob,
        job_id,
    )

def complete_job_successfully(
    db: Session,
    job_id: int,
    exit_code: int = 0,
) -> None:
    stmt = (
        update(SyncJob)
        .where(
            SyncJob.id == job_id,
            SyncJob.status == JobStatus.RUNNING,
        )
        .values(
            status = JobStatus.SUCCESS,
            finished_at = utcnow(),
            exit_code = exit_code,
            error_message = None,
        )
    )

    result = db.execute(stmt)

    if result.rowcount != 1: # type: ignore
        db.rollback()

        raise RuntimeError(
            f"cannot complete sync job {job_id}: "
            "job is not RUNNING"
        )

    db.commit()

def complete_job_with_failure(
    db: Session,
    job_id: int,
    error_message: str,
    exit_code: int | None = None,
) -> None:
    stmt = (
        update(SyncJob)
        .where(
            SyncJob.id == job_id,
            SyncJob.status == JobStatus.RUNNING,
        )
        .values(
            status = JobStatus.FAILED,
            finished_at = utcnow(),
            exit_code = exit_code,
            error_message = error_message,
        )
    )

    result = db.execute(stmt)

    if result.rowcount != 1: # type: ignore
        db.rollback()

        raise RuntimeError(
            f"cannot complete sync job {job_id}: "
            "job is not RUNNING"
        )

    db.commit()


def recover_interrupted_jobs(
    db: Session,
) -> int:
    stmt = (
        update(SyncJob)
        .where(
            SyncJob.status == JobStatus.RUNNING
        )
        .values(
            status=JobStatus.FAILED,
            finished_at=utcnow(),
            error_message=(
                "worker was interrupted "
                "before job completion"
            ),
        )
    )

    result = db.execute(stmt)

    db.commit()

    return result.rowcount # type: ignore
