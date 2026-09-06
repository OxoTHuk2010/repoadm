from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from repoadm.models import (
    Repository,
    RepositoryTarget,
)

from repoadm.schemas import (
    RepositoryTargetCreate,
    RepositoryTargetUpdate,
)

from repoadm.exceptions import (
    RepositoryNotFoundError,
    RepositoryTargetNotFoundError,
    RepositoryTargetConflictError,
)


def get_repository_target(
    db:Session,
    target_id: int,
) -> RepositoryTarget:
    stmt = select(RepositoryTarget).where(
        RepositoryTarget.id == target_id
    )

    target = db.scalar(stmt)

    if target is None:
        raise RepositoryTargetNotFoundError(
            f"Repository target {target_id} not found"
        )

    return target

def create_repository_target(
    db: Session,
    repository_id: int,
    data: RepositoryTargetCreate,
) -> RepositoryTarget:
    repository = db.get(
        Repository,
        repository_id,
    )

    if repository is None:
        raise RepositoryNotFoundError(
            f"repository {repository_id} not found"
        )

    target = RepositoryTarget(
        name = data.name,
        slug = data.slug,

        source_type = data.source_type,
        source_url = data.source_url,

        releasever = data.releasever,
        basearch = data.basearch,
        include_noarch = data.include_noarch,

        storage_path = data.storage_path,

        local_repoid = data.local_repoid,
        local_name = data.local_name,

        source_sslverify = data.source_sslverify,

        local_gpgcheck = data.local_gpgcheck,
        local_gpgkey = data.local_gpgkey,

        enabled = data.enabled,
    )

    db.add(target)

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise RepositoryTargetConflictError(
            "repository target conflicts "
            "with existing data"
        ) from e

    return target

def update_repository_target(
    db: Session,
    target_id: int,
    data: RepositoryTargetUpdate,
) -> RepositoryTarget:
    target = get_repository_target(
        db,
        target_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
    )

    if not changes:
        return target

    for field, value in changes.items():
        setattr(
            target,
            field,
            value,
        )

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise RepositoryTargetConflictError(
            "repository target conflicts "
            "with existing data"
        ) from e

    return target
