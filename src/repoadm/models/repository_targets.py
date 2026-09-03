from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repoadm.database import Base
from repoadm.utils import enum_type, utcnow

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repositories import Repository
    from .sync_jobs import SyncJob
    from .repo_bundles_members import RepositoryBundlesMember

class SourceType(str, Enum):
    BASEURL = "baseurl"
    MIRRORLIST = "mirrorlist"
    METALINK = "metalink"

class RepositoryTarget(Base):
    __tablename__ = "repository_targets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_type: Mapped[SourceType] = mapped_column(
        enum_type(
            SourceType,
            "repository_targets_source_type",
            length=20,
        ),
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    releasever: Mapped[str|None] = mapped_column(
        String(50),
        nullable=True,
    )

    basearch: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="x86_64",
    )

    include_noarch: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    local_repoid: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    local_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_sslverify: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    local_gpgcheck: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    local_gpgkey: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    repository: Mapped["Repository"] = relationship(
        back_populates="targets",
    )

    sync_jobs: Mapped[list["SyncJob"]] = relationship(
        back_populates="repository_target",
    )

    bundle_membership: Mapped[list["RepositoryBundlesMember"]] = relationship(
        back_populates="repository_target",
    )

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "slug",
            name="uq_repository_target_slug",
        ),
    )
