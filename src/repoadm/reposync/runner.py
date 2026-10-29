import shlex
import subprocess
import time

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass(frozen=True, slots=True)
class RepoSyncRunResult:
    exit_code: int
    duration_seconds: float
    log_path: Path

    @property
    def successful(self) -> bool:
        return self.exit_code == 0

class RepoSyncRunner:
    """
    Запускает уже подготовленную команду dnf reposync.
    """
    def run(
        self,
        *,
        argv: list[str],
        log_path: Path,
    ) -> RepoSyncRunResult:
        if not argv:
            raise ValueError(
                "reposync command must not be empty"
            )

        log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        started_at = datetime.now(
            timezone.utc
        )

        started_monotonic = time.monotonic()

        with log_path.open(
            "a",
            encoding="utf-8",
        ) as log_file:

            log_file.write(
                "\n"
                "================================\n"
            )

            log_file.write(
                "Reposync started\n"
            )

            log_file.write(
                f"time={started_at.isoformat()}\n"
            )

            log_file.write(
                f"command={shlex.join(argv)}\n"
            )

            log_file.write(
                "================================\n\n"
            )

            log_file.flush()

            try:
                completed = subprocess.run(
                    argv,
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,

                    shell=False,
                    check=False,
                    text=True,
                )
            except OSError as exc:
                finished_at = datetime.now(
                    timezone.utc
                )

                duration = (
                    time.monotonic()
                    - started_monotonic
                )

                log_file.write(
                    "\n"
                    "========================================\n"
                )

                log_file.write(
                    "RepoSync failed to start\n"
                )

                log_file.write(
                    f"time={finished_at.isoformat()}\n"
                )

                log_file.write(
                    f"duration={duration:.2f}\n"
                )

                log_file.write(
                    f"error={exc}\n"
                )

                log_file.write(
                    "========================================\n"
                )

                log_file.flush()

                raise

            finished_at = datetime.now(
                timezone.utc
            )

            duration = (
                time.monotonic()
                - started_monotonic
            )

            log_file.write(
                "\n"
                "========================================\n"
            )

            log_file.write(
                "RepoSync finished\n"
            )

            log_file.write(
                f"time={finished_at.isoformat()}\n"
            )

            log_file.write(
                f"exit_code={completed.returncode}\n"
            )

            log_file.write(
                f"duration={duration:.2f}\n"
            )

            log_file.write(
                "========================================\n"
            )

            log_file.flush()

        return RepoSyncRunResult(
            exit_code=completed.returncode,
            duration_seconds=duration,
            log_path=log_path,
        )
