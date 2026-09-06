from sqlalchemy.orm import (
    Session,
)
from sqlalchemy.exc import IntegrityError

from repoadm.models import (
    RepositoryTarget,
    RepositoryBundle,
    RepositoryBundlesMember,
)
from repoadm.schemas import (
    RepositoryBundleMemberCreate,
    RepositoryBundleMemberUpdate,
)
from repoadm.services import (
    get_repository_bundle,
)
from repoadm.exceptions import (
    RepositoryBundleNotFoundError,
    RepositoryTargetNotFoundError,
    RepositoryBundleConflictError,
    RepositoryBundleMemberNotFoundError,
)

def add_target_to_bundle(
    db: Session,
    bundle_id: int,
    target_id: int,
    data: RepositoryBundleMemberCreate,
) -> RepositoryBundle:
    bundle = db.get(
        RepositoryBundle,
        bundle_id,
    )

    if bundle is None:
        raise RepositoryBundleNotFoundError(
            f"repository bundle {bundle_id} not found"
        )

    target = db.get(
        RepositoryTarget,
        target_id,
    )

    if target is None:
        raise RepositoryTargetNotFoundError(
            f"repository target {target_id} not found"
        )

    member = RepositoryBundlesMember(
        bundle_id = bundle_id,
        repository_target_id = target_id,
        enabled = data.enabled,
        sort_order = data.sort_order,
    )

    db.add(member)

    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise RepositoryBundleConflictError(
            "repository target is already "
            "a member of this bundle"
        ) from e

    return get_repository_bundle(
        db,
        bundle_id,
    )


def update_bundle_member(
    db: Session,
    bundle_id: int,
    target_id: int,
    data: RepositoryBundleMemberUpdate,
) -> RepositoryBundle:
    member = db.get(
        RepositoryBundlesMember,
        {
            "bundle_id": bundle_id,
            "repository_target_id": target_id,
        },
    )

    if member is None:
        raise RepositoryBundleMemberNotFoundError(
            "repository target is not "
            "a member of this bundle"
        )

    changes = data.model_dump(
        exclude_unset=True,
    )

    for field, value in changes.items():
        setattr(
            member,
            field,
            value,
        )

    db.commit()

    return get_repository_bundle(
        db,
        bundle_id,
    )

def remove_target_from_bundle(
    db: Session,
    bundle_id: int,
    target_id: int,
) -> None:
    member = db.get(
        RepositoryBundlesMember,
        {
            "bundle_id": bundle_id,
            "repository_target_id": target_id,
        },
    )

    if member is None:
        raise RepositoryBundleMemberNotFoundError(
            "repository target is not "
            "a member of this bundle" 
        )

    db.delete(member)
    db.commit()
