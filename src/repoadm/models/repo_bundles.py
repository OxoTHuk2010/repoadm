from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repoadm.database import Base
from repoadm.utils import utcnow

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repo_bundles_members import RepositoryBundlesMember


class RepositoryBundle(Base):
    __tablename__ = "repo_bundles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
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

    members: Mapped[list["RepositoryBundlesMember"]] = relationship(
        back_populates="bundle",
        order_by=(
            "RepositoryBundlesMember.sort_order, "
            "RepositoryBundlesMember.repository_target_id"
        ),
    )
