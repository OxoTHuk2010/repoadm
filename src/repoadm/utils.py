from datetime import datetime, timezone

import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from sqlalchemy import (
    Enum as SAEnum,
)

def utcnow() -> datetime:
    """
    В v1 храним все datetime как native UTC.
    На уровне API позже явно будем трактовать их как UTC.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

def enum_type(enum_class, name: str, length: int = 32):
    """
    Храним в SQLite именно Enum.value, а не имя Python enum member.
    """
    return SAEnum(
        enum_class,
        values_callable=lambda cls: [item.value for item in cls],
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        name=name,
        length=length,
    )

SLUG_RE = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,98}[a-z0-9])?$"
)

REPOID_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$"
)

PATH_SEGMENT_RE = re.compile(
    r"^[A-Za-z0-9._+-]+$"
)

def validate_slug(value: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise ValueError(
            "slug may contain only lowercase letters, "
            "digits and '-'"
        )
    return value


def validate_storage_path(value: str) -> str:
    if not value:
        raise ValueError("storage_path не может быть пустым")

    if value.startswith("/"):
        raise ValueError(
            "storage_path должен быть относительным"
        )

    if "\\" in value:
        raise ValueError(
            "storage_path должен использоваеть '/' разделитель"
        )

    parts = value.split("/")

    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(
            "storage_path содержит некорректные части"
        )

    for part in parts:
        if not PATH_SEGMENT_RE.fullmatch(part):
            raise ValueError(
                f"неверная часть storage_path: {part}"
            )

    path = PurePosixPath(value)

    if path.is_absolute():
        raise ValueError(
            "storage_path должен быть относительным"
        )

    return value

def validate_source_url(value: str) -> str:
    parsed = urlsplit(value)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError(
            "Поддерживаются только http или https репозитории"
        )

    if not parsed.hostname:
        raise ValueError(
            "hostname не может быть пустым"
        )

    #запрет хранения credentials в url
    # https://user:password@repository.example/
    if parsed.username is not None or parsed.password is not None:
        raise ValueError(
            "параметры авторизации запрещено хранить в URL"
        )

    return value

def validate_repoid(value: str) -> str:
    if not REPOID_RE.fullmatch(value):
        raise ValueError(
            "Неверный локальный id репозитория"
        )
    return value