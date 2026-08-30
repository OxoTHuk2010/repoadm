from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repoadm.database import Base
from repoadm.utils import enum_type, utcnow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .repository_targets import RepositoryTarget



class SyncMode(str, Enum):
    SCHEDULED = "SCHEDULED"
    ARCHIVE = "ARCHIVE"
    MANUAL = "MANUAL"  

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    sync_mode: Mapped[SyncMode] = mapped_column(
        enum_type(
            SyncMode,
            "repositories_sync_mode",
            length=20,
        ),
        nullable=False,
    )

    schedule_cron: Mapped[str| None] = mapped_column(
        String(100),
        nullable=True,
    )

    next_run_at: Mapped[str|None] = mapped_column(
        DateTime(),
        nullable=True,
        index=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        dafault=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    targets: Mapped[list["RepositoryTarget"]] = relationship(
        back_populates="repository",
    )

    __mapper_args__ = (
        CheckConstraint(
            """
            (
                sync_mode = 'SCHEDULED'
                AND schedule_cron IS NOT NULL
            )
            OR
            (
                sync_mode IN ('ARCHIVE', 'MANUAL')
                AND schedule_cron IS NULL
            )
            """,
            name="ck_repository_schedule_cron",
        ),
        CheckConstraint(
            """
            (
                sync_mode = 'SCHEDULED'
                OR next_run_at IS NULL
            )
            """,
            name="ck_repository_next_run",
        ),
    )