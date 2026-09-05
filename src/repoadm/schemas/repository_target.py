from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from repoadm.models.repository_targets import SourceType

from repoadm.utils import validate_slug, validate_storage_path, validate_source_url, validate_repoid


class RepositoryTargetCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    slug: str

    source_type: SourceType

    source_url: str

    releasever: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    basearch: str = Field(
        default="x86_64",
        min_length=1,
        max_length=50,
    )

    include_noarch: bool = True

    storage_path: str

    local_repoid: str

    local_name: str = Field(
        min_length=1,
        max_length=255,
    )

    source_sslverify: bool = True

    local_gpgcheck: bool = True

    local_gpgkey: str | None = None

    enabled: bool = True

    @field_validator("slug")
    @classmethod
    def check_slug(cls, value: str) -> str:
        return validate_slug(value)

    @field_validator("storage_path")
    @classmethod
    def check_storage_path(cls, value: str) -> str:
        return validate_storage_path(value)

    @field_validator("source_url")
    @classmethod
    def check_source_url(cls, value: str) -> str:
        return validate_source_url(value)

    @field_validator("local_repoid")
    @classmethod
    def check_repoid(cls, value: str) -> str:
        return validate_repoid(value)

class RepositoryTargetResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    repository_id: int

    name: str
    slug: str

    source_type: SourceType
    source_url: str

    releasever: str | None
    basearch: str
    include_noarch: bool

    storage_path: str

    local_repoid:str
    local_name: str

    source_sslverify: bool

    local_gpgcheck: bool
    local_gpgkey: str | None

    enabled: bool

class RepositoryTargetUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    source_type: SourceType | None = None
    source_url: str | None = None

    releasever: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    basearch: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    include_noarch: bool | None = None

    storage_path: str | None = None

    local_repoid:str | None = None
    local_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    source_sslverify: bool | None = None

    local_gpgcheck: bool | None = None
    local_gpgkey: str | None = None

    enabled: bool | None = None

    @field_validator("source_url")
    @classmethod
    def check_source_url(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_source_url(value)

    @field_validator("storage_path")
    @classmethod
    def check_storage_path(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_storage_path(value)

    @field_validator("local_repoid")
    @classmethod
    def check_local_repoid(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_repoid(value)
