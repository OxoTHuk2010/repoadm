from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from datetime import datetime

from repoadm.models.repositories import SyncMode
from repoadm.utils import validate_slug

from .repository_target import RepositoryTargetCreate, RepositoryTargetResonce


class RepositoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    slug: str

    sync_mode: SyncMode

    schedule_cron: str | None = Field(
        default=None,
        max_length=100,
    )

    enabled: bool = True

    targets: list[RepositoryTargetCreate] = Field(
        max_length=1,
    )

    @field_validator("slug")
    @classmethod
    def check_slug(cls, value: str) -> str:
        return validate_slug(value)

    @field_validator("schedule_cron")
    @classmethod
    def normalize_cron(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "schedule_cron не может быть пустым"
            )

        return value

    @model_validator(mode='after')
    def check_schedule(self):
        if self.sync_mode == SyncMode.SCHEDULED:
            if self.schedule_cron is None:
                raise ValueError(
                    "SCHEDULED репозиторий должен иметь заполненный schedule_cron"
                )
        else:
            if self.schedule_cron is not None:
                raise ValueError(
                    "schedule_cron необходим к заполнению"
                    "если репозиторий SCHEDULED"
                )

        return self

class RepositoryUpdate(BaseModel):
    name: str | None = Field(
        default = None,
        min_length=1,
        max_length=255,
    )

    sync_mode: SyncMode | None = None

    schedule_cron: str | None = Field(
        default=None,
        max_length=100,
    )

    enabled: bool | None = None

    @field_validator("schedule_cron")
    @classmethod
    def normalize_cron(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "schedule_cron не может быть пустым"
            )

        return value

class RepositoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str
    slug: str

    sync_mode: SyncMode

    schedule_cron: str | None
    next_run_at: datetime | None

    enabled: bool

    targets: list[RepositoryTargetResonce]
