from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from repoadm.models import (
    JobStatus,
    SyncJob,
    JobTrigger,
    RepositoryTarget,
)

from repoadm.services import (
    get_repository,
)

from repoadm.exceptions import(
    SyncAlreadyPendingError,
    RepositoryDisabledError,
    RepositoryTargetDisabledError,
    RepositoryHasNoEnabledTargetsError,
    RepositoryNotFoundError,
    RepositoryTargetNotFoundError,
    SyncJobNotFoundError,
)

from uuid import uuid4

ACTIVE_JOB_STATUSES = (
    JobStatus.QUEUED,
    JobStatus.RUNNING,
)


def get_active_job_for_target(
    db: Session,
    target_id: int,
) -> SyncJob | None:
    stmt = (
        select(SyncJob)
        .where(
            SyncJob.repository_target_id == target_id,
            SyncJob.status.in_(ACTIVE_JOB_STATUSES),
        )
        .order_by(SyncJob.id)
    )

    return db.scalar(stmt)

def enqueue_target_sync(
    db: Session,
    target_id: int,
) -> SyncJob:

    target = db.get(
        RepositoryTarget,
        target_id,
    )

    if target is None:
        raise RepositoryTargetNotFoundError(
            f"repository target {target_id} not found"
        )

    if not target.enabled:
        raise RepositoryTargetDisabledError(
            f"repository target {target_id} is disabled"
        )

    repository = target.repository

    if not repository.enabled:
        raise RepositoryDisabledError(
            f"repository {repository.id} is disabled"
        )

    active_job = get_active_job_for_target(
        db,
        target.id,
    )

    if active_job is not None:
        raise SyncAlreadyPendingError(
            f"repository target {target.id} "
            f"already has active job {active_job.id}"
        )

    job = SyncJob(
        repository_target_id = target.id,
        batch_id = str(uuid4()),
        trigger = JobTrigger.MANUAL,
        status = JobStatus.QUEUED,
    )

    db.add(job)

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        ## Мог сработать partial UNIQUE
        ## наружу не отдаём
        raise SyncAlreadyPendingError(
            f"repository target {target.id} "
            "already has an active sync job"
        ) from e

    db.refresh(job)

    return job


def enqueu_repository_sync(
    db: Session,
    repository_id: int,
) -> tuple[str, list[SyncJob], list[int]]:

    repository = get_repository(
        db,
        repository_id,
    )

    if repository is None:
        raise RepositoryNotFoundError(
            f"repository {repository.id} not found"
        )

    if not repository.enabled:
        raise RepositoryDisabledError(
            f"repository {repository.id} is disabled"
        )

    targets = [
        target
        for target in repository.targets
        if target.enabled
    ]

    if not targets:
        raise RepositoryHasNoEnabledTargetsError(
            "repository has no enabled targets"
        )

    batch_id = str(uuid4())

    created_jobs: list[SyncJob] = []
    skipped_target_ids: list[int] = []

    for target in targets:

        job = SyncJob(
            repository_target_id = target.id,
            batch_id = batch_id,
            trigger = JobTrigger.MANUAL,
            status = JobStatus.QUEUED,
        )

        try:
            with db.begin_nested():
                db.add(job)
                db.flush()

        except IntegrityError:
            skipped_target_ids.append(
                target.id
            )
            continue

        created_jobs.append(job)

    if not created_jobs:
        db.rollback()

        raise SyncAlreadyPendingError(
            "all enabled repository targets "
            "already have active sync jobs"
        )

    db.commit()

    return (
        batch_id,
        created_jobs,
        skipped_target_ids,
    )


def get_sync_job(
    db:Session,
    job_id: int,
) -> SyncJob:

    job = db.get(
        SyncJob,
        job_id,
    )

    if job is None:
        raise SyncJobNotFoundError(
            f"sync job {job_id} not found"
        )

    return job

def list_sync_jobs(
    db:Session,
    status: JobStatus | None = None,
    target_id: int | None = None,
    batch_id: str | None = None,
    limit: int = 100,
) -> list[SyncJob]:

    stmt = (
        select(SyncJob)
        .order_by(
            SyncJob.created_at.desc(),
            SyncJob.id.desc(),
        )
        .limit(limit)
    )

    if status is not None:
        stmt = stmt.where(
            SyncJob.status == status
        )

    if target_id is not None:
        stmt = stmt.where(
            SyncJob.repository_target_id
            == target_id
        )

    if batch_id is not None:
        stmt = stmt.where(
            SyncJob.batch_id == batch_id
        )

    return list(
        db.scalars(stmt).all()
    )

def get_queue_stats(
    db: Session,
) -> dict:

    queued = db.scalar(
        select(func.count())
        .select_from(SyncJob)
        .where(
            SyncJob.status == JobStatus.QUEUED
        )
    ) or 0

    running = db.scalar(
        select(func.count())
        .select_from(SyncJob)
        .where(
            SyncJob.status == JobStatus.RUNNING
        )
    ) or 0

    oldest_queued_at = db.scalar(
        select(
            func.min(
                SyncJob.created_at
            )
        )
        .where(
            SyncJob.status == JobStatus.QUEUED
        )
    )

    return {
        "queued": queued,
        "running": running,
        "oldest_queued_at": oldest_queued_at,
    }

