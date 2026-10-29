from dataclasses import dataclass

from repoadm.models import SourceType

@dataclass(frozen=True, slots=True)
class RepoSyncTargetConfig:
    target_id: int

    source_type: SourceType
    source_url: str

    releasever: str | None
    basearch: str
    include_noarch: bool

    source_sslverify: bool

    storage_path: str
