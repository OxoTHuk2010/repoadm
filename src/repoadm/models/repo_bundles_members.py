from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Index,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repoadm.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repo_bundles import RepositoryBundle
    from .repository_targets import RepositoryTarget


class RepositoryBundlesMember(Base):
    __tablename__ = "repo_bundle_members"

    bundle_id: Mapped[int] = mapped_column(
        ForeignKey("repo_bundles.id"),
        primary_key=True,
    )

    repository_target_id: Mapped[int] = mapped_column(
        ForeignKey("repository_targets.id"),
        primary_key=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )

    bundle: Mapped["RepositoryBundle"] = relationship(
        back_populates="members",
    )

    repository_target: Mapped["RepositoryTarget"] = relationship(
        back_populates="bundle_membership",
    )

    __table_args__ = (
        Index(
            "ix_repo_bundle_members_sort",
            "bundle_id",
            "sort_order",
        ),
    )
