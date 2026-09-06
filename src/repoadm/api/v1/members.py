from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from  sqlalchemy.orm import Session

from repoadm.database import get_db
from repoadm.schemas import (
    RepositoryBundleResponse,
    RepositoryBundleMemberCreate,
    RepositoryBundleMemberUpdate,
)
from repoadm.services import (
    add_target_to_bundle,
    update_bundle_member,
    remove_target_from_bundle,
)
from repoadm.exceptions import (
    RepositoryBundleConflictError,
    RepositoryBundleNotFoundError,
    RepositoryTargetNotFoundError,
    RepositoryBundleMemberNotFoundError,
)

router = APIRouter(
    prefix="/api/v1/bundles",
    tags=["repository members"],
)

@router.post(
    "/{bundle_id}/targets/{target_id}",
    response_model=RepositoryBundleResponse,
)
def add_bundle_target_endpoint(
    bundle_id: int,
    target_id: int,
    data: RepositoryBundleMemberCreate,
    db: Session = Depends(get_db),
):
    try:
        return add_target_to_bundle(
            db,
            bundle_id,
            target_id,
            data,
        )
    except RepositoryBundleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_BUNDLE_NOT_FOUND",
                "message": str(e),
            },
        ) from e
    except RepositoryTargetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e
    except RepositoryBundleConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_BUNDLE_MEMBER_CONFLICT",
                "message": str(e),
            },
        ) from e

@router.patch(
    "/{bundle_id}/targets/{target_id}",
    response_model=RepositoryBundleResponse,
)
def update_bundle_target_endpoint(
    bundle_id: int,
    target_id: int,
    data: RepositoryBundleMemberUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_bundle_member(
            db,
            bundle_id,
            target_id,
            data,
        )
    except RepositoryBundleMemberNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_BUNDLE_MEMBER_NOT_FOUND",
                "message": str(e),
            },
        ) from e

@router.delete(
    "/{bundle_id}/targets/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_bundle_target_endpoint(
    bundle_id: int,
    target_id: int,
    db: Session = Depends(get_db),
):
    try:
        remove_target_from_bundle(
            db,
            bundle_id,
            target_id,
        )
    except RepositoryBundleMemberNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_BUNDLE_MEMBER_NOT_FOUND",
                "message": str(e),
            },
        ) from e

    return Response(
        status.HTTP_204_NO_CONTENT
    )
