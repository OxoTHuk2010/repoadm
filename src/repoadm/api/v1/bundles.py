from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from  sqlalchemy.orm import Session

from repoadm.database import get_db
from repoadm.schemas import (
    RepositoryBundleResponse,
    RepositoryBundleCreate,
    RepositoryBundleUpdate,
)
from repoadm.services import (
    create_repository_bundle,
    list_repository_bundles,
    get_repository_bundle,
    update_repository_bundle,
)
from repoadm.exceptions import (
    RepositoryBundleConflictError,
    RepositoryBundleNotFoundError,
)

router = APIRouter(
    prefix="/api/v1/bundles",
    tags=["repository bundles"],
)

@router.post(
    "",
    response_model=RepositoryBundleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bundle_endpoint(
    data: RepositoryBundleCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_repository_bundle(
            db,
            data,
        )

    except RepositoryBundleConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_BUNDLE_CONFLICT",
                "message": str(e),
            },
        ) from e

@router.get(
    "",
    response_model=list[RepositoryBundleResponse],
)
def list_bundle_endpoind(
    enabled: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    return list_repository_bundles(
        db,
        enabled = enabled,
    )

@router.get(
    "/{bundle_id}",
    response_model=RepositoryBundleResponse,
)
def get_bundle_endpoint(
    bundle_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_repository_bundle(
            db,
            bundle_id,
        )
    except RepositoryBundleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_BUNDLE_NOT_FOUND",
                "message": str(e),
            },
        ) from e

@router.patch(
    "/{bundle_id}",
    response_model=RepositoryBundleResponse,
)
def update_bundle_endpoint(
    bundle_id: int,
    data: RepositoryBundleUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_repository_bundle(
            db,
            bundle_id,
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
    except RepositoryBundleConflictError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "REPOSITORY_BUNDLE_CONFLICT",
                    "message": str(e),
                },
            ) from e
