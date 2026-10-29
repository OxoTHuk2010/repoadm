from pathlib import Path

class InvalidRepositoryPathError(RuntimeError):
    pass

def resolve_repository_destination(
    repository_root: Path,
    storage_path: str,
) -> Path:
    root = repository_root.resolve()

    destination = (
        root
        / storage_path
    ).resolve()

    try:
        destination.relative_to(root)

    except ValueError as e:
        raise InvalidRepositoryPathError(
            "repository destination escapes "
            "repository root"
        ) from e

    return destination
