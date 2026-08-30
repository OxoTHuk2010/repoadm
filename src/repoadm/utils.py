from datetime import datetime, timezone

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
