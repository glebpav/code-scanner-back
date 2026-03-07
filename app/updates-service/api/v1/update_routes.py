from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import Response
from starlette import status

from dependencies import get_update_service
from scheme.update_scheme import CreateUpdateVersionRequest, UpdateVersionResponse
from service.update_service import UpdateService

router = APIRouter(prefix="/updates", tags=["Updates"])


def _to_response(version) -> UpdateVersionResponse:
    return UpdateVersionResponse(
        version_number=version.version_number,
        description=version.description,
        created_at=version.created_at,
        file_keys=[file_entity.s3_key for file_entity in version.files],
    )


@router.post(
    "/versions",
    response_model=UpdateVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_update_version(
        create_update_version_request: CreateUpdateVersionRequest,
        update_service: UpdateService = Depends(get_update_service),
) -> UpdateVersionResponse:
    created_version = await update_service.create_update_version(
        create_update_version_request=create_update_version_request,
    )
    return _to_response(created_version)


@router.get(
    "/versions",
    response_model=list[UpdateVersionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_update_versions(
        update_service: UpdateService = Depends(get_update_service),
) -> list[UpdateVersionResponse]:
    versions = await update_service.get_all_update_versions()
    return [_to_response(version) for version in versions]


@router.get(
    "/versions/latest/download",
    status_code=status.HTTP_200_OK,
)
async def download_latest_update_archive(
        update_service: UpdateService = Depends(get_update_service),
) -> Response:
    archive_bytes, filename = await update_service.download_latest_update_archive()
    return Response(
        content=archive_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get(
    "/versions/{version_number}/download",
    status_code=status.HTTP_200_OK,
)
async def download_update_archive_by_version(
        version_number: int,
        update_service: UpdateService = Depends(get_update_service),
) -> Response:
    archive_bytes, filename = await update_service.download_update_archive_by_version(version_number)
    return Response(
        content=archive_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )