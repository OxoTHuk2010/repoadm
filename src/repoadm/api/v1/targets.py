from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from repoadm.database import get_db
from repoadm.schemas import (
    RepositoryTargetCreate,
    RepositoryTargetUpdate,
    RepositoryTargetResponse,
)
from repoadm.services import (
    RepositoryNotFoundError,
    RepositoryTargetConflictError,
    RepositoryTargetNotFoundError,
    create_repository_target,
    get_repository_target,
    update_repository_target,
)

router = APIRouter(
    tags=["repository targets"],
)

@router.post(
    "/api/v1/repositories/{repository_id}/targets",
    response_model=RepositoryTargetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_target_endpoint(
    repository_id: int,
    data: RepositoryTargetCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_repository_target(
            db,
            repository_id,
            data,
        )
    except RepositoryTargetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e

    except RepositoryTargetConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_TARGET_CONFLICT",
                "message": str(e),
            },
        )

@router.get(
    "/api/v1/targets/{target_id}",
    response_model=RepositoryTargetResponse,
)
def get_target_endpoint(
    target_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_repository_target(
            db,
            target_id,
        )
    except RepositoryTargetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e

@router.patch(
    "/api/v1/targets/{target_id}",
    response_model=RepositoryTargetUpdate,
)
def update_target_endpoint(
    target_id: int,
    data: RepositoryTargetUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_repository_target(
            db,
            target_id,
            data,
        )

    except RepositoryTargetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e

    except RepositoryTargetConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_TARGET_CONFLICT",
                "message": str(e),
            },
        )
