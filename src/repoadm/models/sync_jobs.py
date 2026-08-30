from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    String,
    ForeignKey,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repoadm.database import Base
from repoadm.utils import enum_type, utcnow

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repository_targets import RepositoryTarget


class JobTrigger(str, Enum):
    INITIAL = "INITIAL"
    SCHEDULE = "SCHEDULE"
    MANUAL = "MANUAL"

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    repository_target_id: Mapped[int] = mapped_column(
        ForeignKey("repository_targets.id"),
        nullable=False,
    )

    batch_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    trigger: Mapped[JobTrigger] = mapped_column(
        enum_type(
            JobTrigger,
            "sync_jobs_trigger",
            length=20,
        ),
        nullable=False,
    )

    status: Mapped[JobStatus] = mapped_column(
        enum_type(
            JobStatus,
            "sync_jobs_status",
            length=20,
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utcnow,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
    )

    exit_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    log_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    repository_target: Mapped["RepositoryTarget"] = relationship(
        back_populates="sync_jobs",
    )

    __table_args__ = (
        # FIFO queue
        Index(
            "ix_sync_jobs_status_created",
            "status",
            "created_at",
        ),

        # История конкретного target
        Index(
            "ix_sync_jobs_target_created",
            "repository_target_id",
            "created_at",
        ),

        # Ограничение: один Target не может иметь
        # одновременно два QUEUED/RUNNING jobs.
        Index(
            "uq_sync_jobs_active_target",
            "repository_target_id",
            unique=True,
            sqlite_where=text(
                "status IN ('QUEUED', 'RUNNING')"
            ),
        ),
    )
