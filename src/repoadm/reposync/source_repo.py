import os
import tempfile
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from repoadm.reposync.types import RepoSyncTargetConfig

@dataclass(frozen=True, slots=True)
class SourceRepoConfig:
    repo_id: str
    directory: Path
    file_path: Path


def get_source_repo_id(
    target_id: int,
) -> str:
    return f"repoadm-target-{target_id}"

def write_source_repo_config(
    target: RepoSyncTargetConfig,
    source_config_root: Path,   
) -> SourceRepoConfig:
    if "\n" in target.source_url or "\r" in target.source_url:
        raise ValueError(
            "source_url must not contain newline characters"
        )

    repo_id = get_source_repo_id(
        target.target_id
    )

    target_directory = (
        source_config_root
        / "targets"
        / str(target.target_id)
    )

    target_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        target_directory
        / "source.repo"
    )

    config = ConfigParser(
        interpolation=None,
    )

    config[repo_id] = {
        "name": f"RepoADM target {target.target_id}",

        target.source_type.value:
            target.source_url,

        "enabled": "1",

        "sslverify":
            "1"
            if target.source_sslverify
            else "0",

        "gpgcheck": "0",
        "repo_gpgcheck": "0",

        "skip_if_unavailable": "0",
    }

    fd, temporary_name = tempfile.mkstemp(
        prefix=".source.repo.",
        dir=target_directory,
        text=True,
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:
            config.write(file)

            file.flush()
            os.fsync(
                file.fileno()
            )

        os.replace(
            temporary_name,
            destination,
        )

    except Exception:
        try:
            os.unlink(
                temporary_name
            )
        except FileNotFoundError:
            pass

        raise

    return SourceRepoConfig(
        repo_id=repo_id,
        directory=target_directory,
        file_path=destination,
    )
