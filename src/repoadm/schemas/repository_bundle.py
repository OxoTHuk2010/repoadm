from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from repoadm.schemas.repository_bundle_member import (
    RepositoryBundleMemberResponse,
)
from repoadm.utils import validate_repo_filename

class RepositoryBundleCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    filename: str

    enabled: bool = True

    @field_validator("filename")
    @classmethod
    def check_filename(
        cls,
        value: str,
    ) -> str:
        return validate_repo_filename(value)

class RepositoryBundleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    filename: str | None = None

    enabled: bool | None = None

    @field_validator("filename")
    @classmethod
    def check_filename(
        cls,
        value: str,
    ) -> str | None:
        if value is None:
            return None
        
        return validate_repo_filename(value)    

class RepositoryBundleResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str
    filename: str
    enabled: bool

    created_at: datetime
    updated_at: datetime

    members: list[RepositoryBundleMemberResponse]
