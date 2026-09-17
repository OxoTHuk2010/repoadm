from pathlib import Path
from repoadm.config import settings

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from repoadm.models import (
    JobStatus,
    SyncJob,
)

def get_job_log_path(
    job_id: int,
) -> Path:
    return(
        Path(settings.job_log_root)
        /"jobs"
        /f"{job_id}.log"
    )

def create_job_log(
    job_id: int,
) -> str:
    relative_path = Path(
        "jobs",
        f"{job_id}.log",
    )

    absolute_path = (
        Path(settings.job_log_root)
        / relative_path
    )

    absolute_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    absolute_path.touch(
        exist_ok=True,
    )

    return str(relative_path)

def set_job_log_path(
    db: Session,
    job_id: int,
    log_path: str,
) -> None:
    db.execute(
        update(SyncJob)
        .where(
            SyncJob.id == job_id
        )
        .values(
            log_path=log_path
        )
    )

    db.commit()
