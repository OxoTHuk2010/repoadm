from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from repoadm.models import (
    Repository,
    RepositoryTarget,
    SyncMode,
)

from repoadm.schemas import (
    RepositoryCreate,
    RepositoryUpdate,
)

class RepositoryNotFoundError(Exception):
    pass

class RepositoryConflictError(Exception):
    pass

class RepositoryConfigurationError(Exception):
    pass

def get_repository(
    db: Session,
    repository_id: int,
) -> Repository:
    stmt = (
        select(Repository)
        .options(
            selectinload(Repository.targets)
        )
        .where(
            Repository.id == repository_id
        )
    )

    repository = db.scalar(stmt)

    if repository is None:
        raise RepositoryNotFoundError(
            f"repository {repository_id} not found"
        )

    return repository

def list_repositories(
    db: Session,
    enabled: bool | None = None,
) -> list[Repository]:
    stmt = (
        select(Repository)
        .options(
            selectinload(Repository.targets)
        )
        .order_by(Repository.id)
    )

    if enabled is not None:
        stmt = stmt.where(
            Repository.enabled.is_(enabled)
        )

    return list(
        db.scalars(stmt).all()
    )

def create_repository(
    db: Session,
    data: RepositoryCreate,
) -> Repository:
    repository = Repository(
        name = data.name,
        slug = data.slug,
        sync_mode = data.sync_mode,
        schedule_cron = data.schedule_cron,
        enabled = data.enabled,
    )

    for target_data in data.targets:
        target = RepositoryTarget(
            name = target_data.name,
            slug = target_data.slug,

            source_type = target_data.source_type,
            source_url = target_data.source_url,

            releasever = target_data.releasever,
            basearch = target_data.basearch,
            include_noarch = target_data.include_noarch,

            storage_path = target_data.storage_path,

            local_repoid = target_data.local_repoid,
            local_name = target_data.local_name,

            source_sslverify = target_data.source_sslverify,

            local_gpgcheck = target_data.local_gpgcheck,
            local_gpgkey = target_data.local_gpgkey,

            enabled = target_data.enabled,
        )

        repository.targets.append(target)

    db.add(repository)

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise RepositoryConflictError(
            "repository conflict with existing data"
        ) from e

    return get_repository(
        db,
        repository.id,
    )

def update_repository(
    db: Session,
    repository_id: int,
    data: RepositoryUpdate,
) -> Repository:
    repository = get_repository(
        db,
        repository_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
    )

    if not changes:
        return repository

    #Если переключаемся с SCHEDULED на другой режим, очищаем расписание
    if (
        "sync_mode" in changes
        and changes["sync_mode"] != SyncMode.SCHEDULED
        and "schedule_cron" not in changes
    ):
        changes["schedule_cron"] = None

    effective_sync_mode = changes.get(
        "sync_mode",
        repository.sync_mode,
    )

    effective_schedule = changes.get(
        "schedule_cron",
        repository.schedule_cron,
    )

    if effective_sync_mode == SyncMode.SCHEDULED:
        if effective_schedule is None:
            raise RepositoryConfigurationError(
                "SCHEDULED repository requires "
                "schedule_cron"
            )
    else:
        if effective_schedule is not None:
            raise RepositoryConfigurationError(
                "schedule_cron is allowed only "
                "for SCHEDULED repositories"
            )

    for field, value in changes.items():
        setattr(
            repository,
            field,
            value,
        )

    #Scheduler будет рассчитывать это значение заново.
    if (
        "sync_mode" in changes
        or "schedule_cron" in changes
    ):
        repository.next_run_at = None

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise RepositoryConflictError(
            "repository update conflicts "
            "with existing data"
        ) from e

    return get_repository(
        db,
        repository.id,
    )