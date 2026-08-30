from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from repoadm.config import settings

class Base(DeclarativeBase):
    pass

def build_engine(database_url: str) -> Engine:
    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 5,
        },
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()

        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA busy_timeout = 50000")

        cursor.close()

    return engine

engine = build_engine(settings.database_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

def init_db() -> None:
    import repoadm.models #noqa: F401

    Base.metadata.create_all(bind=engine)
