from datetime import datetime
from pydantic import BaseModel, ConfigDict

from repoadm.models import (
    JobStatus,
    JobTrigger,
)

class SyncJobResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    repository_target_id: int

    batch_id: str

    trigger: JobTrigger
    status: JobStatus

    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    exit_code: int | None
    log_path: str | None
    error_message: str | None


class RepositorySyncResponse(BaseModel):
    batch_id: str

    created: list[SyncJobResponse]

    skipped_target_ids: list[int]


class QueueStatsResponse(BaseModel):
    queued: int
    running: int

    oldest_queued_at: datetime | None
