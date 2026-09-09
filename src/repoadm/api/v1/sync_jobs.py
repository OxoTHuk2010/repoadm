from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
)
from sqlalchemy.orm import Session

from repoadm.database import get_db
from repoadm.schemas import (
    SyncJobResponse,
    RepositorySyncResponse,
    QueueStatsResponse,
)
from repoadm.models import JobStatus
from repoadm.services import (
    enqueue_target_sync,
    enqueu_repository_sync,
    list_sync_jobs,
    get_sync_job,
    get_queue_stats,
)
from repoadm.exceptions import (
    RepositoryTargetNotFoundError,
    RepositoryTargetDisabledError,
    RepositoryNotFoundError,
    RepositoryHasNoEnabledTargetsError,
    RepositoryDisabledError,
    SyncAlreadyPendingError,
    SyncJobNotFoundError,
)

router = APIRouter(
    tags=["sync jobs"],
)

@router.post(
    "/api/v1/targets/{target_id}/sync",
    response_model=SyncJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def sync_target_endpoint(
    target_id: int,
    db: Session = Depends(get_db)
):
    try:
        return enqueue_target_sync(
            db,
            target_id,
        )

    except RepositoryTargetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_TARGET_NOT_FOUND",
                "message": str(e),
            },
        ) from e

    except RepositoryTargetDisabledError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_TARGET_DISABLED",
                "message": str(e),
            },
        ) from e

    except RepositoryDisabledError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_DISABLED",
                "message": str(e),
            },
        ) from e

    except SyncAlreadyPendingError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "SYNC_ALREADY_PENDING",
                "message": str(e),
            },
        ) from e


@router.post(
    "/api/v1/reoisutories/{repository_id}/sync",
    response_model=RepositorySyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def sync_repository_endpoint(
    repository_id: int,
    db: Session = Depends(get_db),
):
    try:
        (
            batch_id,
            created,
            skipped,
        ) = enqueu_repository_sync(
            db,
            repository_id,
        )

        return {
            "batch_id": batch_id,
            "created": created,
            "skipped_target_ids": skipped,
            }
        
    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e
    except RepositoryHasNoEnabledTargetsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "NO_ENABLED_TARGETS",
                "message": str(e),
            },
        ) from e

    except RepositoryDisabledError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_DISABLED",
                "message": str(e),
            },
        ) from e

    except SyncAlreadyPendingError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "SYNC_ALREADY_PENDING",
                "message": str(e),
            },
        ) from e

@router.get(
    "/api/v1/jobs",
    response_model=list[SyncJobResponse],
)
def list_jobs_endpoint(
    status_filter: JobStatus | None = Query(
        default=None,
        alias="status",
    ),
    target_id: int | None = None,
    batch_id: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    return list_sync_jobs(
        db,
        status=status_filter,
        target_id=target_id,
        batch_id=batch_id,
        limit=limit,
    )

@router.get(
    "/api/v1/jobs/{job_id}",
    response_model=SyncJobResponse,
)
def get_job_endpoint(
    job_id: int,
    db: Session = Depends(get_db)
):
    try:
        return get_sync_job(
            db,
            job_id,
        )

    except SyncJobNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SYNC_JOB_NOT_FOUND",
                "message": str(e),
            },
        ) from e

@router.get(
    "/api/v1/queue",
    response_model=QueueStatsResponse,
)
def get_queue_endpoint(
    db: Session = Depends(get_db),
):
    return get_queue_stats(db)
