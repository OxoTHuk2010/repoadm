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


class RepositoryTarget(Base):
    __tablename__ = "repository_targets"
    pass
