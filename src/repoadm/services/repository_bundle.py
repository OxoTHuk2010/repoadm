from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from sqlalchemy.exc import IntegrityError

from repoadm.models import (
    RepositoryBundle,
    RepositoryBundlesMember,
)
from repoadm.schemas import (
    RepositoryBundleCreate,
    RepositoryBundleUpdate,
)
from repoadm.exceptions import (
    RepositoryBundleNotFoundError,
    RepositoryBundleConflictError,
)

def get_repository_bundle(
    db: Session,
    bundle_id: int,
) -> RepositoryBundle:
    stmt = (
        select(RepositoryBundle)
        .options(
            selectinload(
                RepositoryBundle.members
            ).selectinload(
                RepositoryBundlesMember.repository_target
            )
        )
        .where(
            RepositoryBundle.id == bundle_id
        )
    )

    bundle = db.scalar(stmt)

    if bundle is None:
        raise RepositoryBundleNotFoundError(
            f"repository bundle {bundle_id} not found"
        )

    return bundle

def list_repository_bundles(
    db: Session,
    enabled: bool | None = None,
) -> list[RepositoryBundle]:
    stmt = (
        select(RepositoryBundle)
        .options(
            selectinload(
                RepositoryBundle.members
            ).selectinload(
                RepositoryBundlesMember.repository_target
            )
        )
        .order_by(
            RepositoryBundle.id
        )
    )

    if enabled is not None:
        stmt = stmt.where(
            RepositoryBundle.enabled.is_(enabled)
        )

    return list(
        db.scalars(stmt).all()
    )

def create_repository_bundle(
    db: Session,
    data: RepositoryBundleCreate
) -> RepositoryBundle:
    bundle = RepositoryBundle(
        name = data.name,
        filename = data.filename,
        enabled = data.enabled,
    )

    db.add(bundle)

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise RepositoryBundleConflictError(
            "repository bundle conflicts"
            "with existing data"
        ) from e

    return get_repository_bundle(
        db,
        bundle.id,
    )

def update_repository_bundle(
    db: Session,
    bundle_id: int,
    data: RepositoryBundleUpdate,
) -> RepositoryBundle:
    bundle = get_repository_bundle(
        db,
        bundle_id,
    )

    changes = data.model_dump(
        exclude_unset=True,
    )

    if not changes:
        return bundle

    for field, value in changes.items():
        setattr(
            bundle,
            field,
            value,
        )

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()

        raise RepositoryBundleConflictError(
            "repository bundle update conflicts "
            "with existing data"
        ) from e

    return get_repository_bundle(
        db,
        bundle_id,
    )
