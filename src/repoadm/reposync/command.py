from pathlib import Path
from repoadm.reposync.source_repo import SourceRepoConfig
from repoadm.reposync.types import RepoSyncTargetConfig

def build_reposync_command(
        *,
        dnf_binary: str,
        target: RepoSyncTargetConfig,
        source_repo: SourceRepoConfig,
        destination: Path,
) -> list[str]:
    argv = [
        dnf_binary,

        "--refresh",

        (
            "--setopt="
            f"reposdir={source_repo.directory}"
        ),

        "--disablerepo=*",

        (
            "--enablerepo="
            f"{source_repo.repo_id}"
        ),
    ]

    if target.releasever is not None:
        argv.append(
            f"--releasever={target.releasever}"
        )

    if target.basearch:
        argv.append(
            f"--forcearch={target.basearch}"
        )

    argv.extend(
        [
            "reposync",

            (
                "--repoid="
                f"{source_repo.repo_id}"
            ),

            (
                "--download-path="
                f"{destination}"
            ),

            "--norepopath",

            "--download-metadata",

            "--remote-time",

            f"--arch={target.basearch}",
        ]
    )

    if target.include_noarch:
        argv.append(
            "--arch=noarch"
        )

    return argv
