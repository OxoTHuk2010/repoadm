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
    RepositoryCreate,
    RepositoryResponse,
    RepositoryUpdate,
)
from repoadm.services import (
    RepositoryConfigurationError,
    RepositoryConflictError,
    RepositoryNotFoundError,
    create_repository,
    get_repository,
    list_repositories,
    update_repository,
)


router = APIRouter(
    prefix="/api/v1/repositories",
    tags=["repositories"],
)


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repository_endpoint(
    data: RepositoryCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_repository(
            db,
            data,
        )
    except RepositoryConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_CONFLICT",
                "message": str(e),
            },
        ) from e

@router.get(
    "",
    response_model=list[RepositoryResponse],
)
def list_repositories_endpoint(
    enabled: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    return list_repositories(
        db,
        enabled=enabled,
    )

@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository_endpoint(
    repository_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_repository(
            db,
            repository_id,
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e

@router.patch(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def update_repository_endpoint(
    repository_id: int,
    data: RepositoryUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_repository(
            db,
            repository_id,
            data,
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "REPOSITORY_NOT_FOUND",
                "message": str(e),
            },
        ) from e

    except RepositoryConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "REPOSITORY_CONFLICT",
                "message": str(e),
            },
        ) from e

    except RepositoryConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "REPOSITORY_CONFIGURATION_INVALID",
                "message": str(e),
            },
        ) from e
