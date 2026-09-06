from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from repoadm.schemas import (
    RepositoryTargetResponse,
)

class RepositoryBundleMemberCreate(BaseModel):
    enabled: bool = True

    sort_order: int = Field(
        default=100,
        ge=0,
        le=1_000_000,
    )

class RepositoryBundleMemberUpdate(BaseModel):
    enabled: bool | None = None

    sort_order: int | None = Field(
        default=None,
        ge=0,
        le=1_000_000,
    )

class RepositoryBundleMemberResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    repository_target_id: int

    enabled: bool
    sort_order: int

    repository_target: RepositoryTargetResponse
