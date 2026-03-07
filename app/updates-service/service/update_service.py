from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

from shared_lib.db.models.update_version import UpdateVersion, UpdateVersionFile
from shared_lib.db.repositories.update_version.update_version_repository import UpdateVersionRepository
from shared_lib.s3 import S3Client

from config import Config
from exception.update_exception import (
    UpdateArchiveBuildException,
    UpdateFileNotFoundException,
    UpdateVersionNotFoundException,
)
from scheme.update_scheme import CreateUpdateVersionRequest


class UpdateService:
    def __init__(
            self,
            config: Config,
            update_version_repository: UpdateVersionRepository,
            s3_client: S3Client,
    ):
        self.__config = config
        self.__update_version_repository = update_version_repository
        self.__s3_client = s3_client

    async def create_update_version(
            self,
            create_update_version_request: CreateUpdateVersionRequest,
    ) -> UpdateVersion:
        update_version_entity = UpdateVersion(
            description=create_update_version_request.description,
            files=[
                UpdateVersionFile(
                    s3_key=file_key,
                    position=index,
                )
                for index, file_key in enumerate(create_update_version_request.file_keys)
            ],
        )

        created_update_version = await self.__update_version_repository.create(
            update_version=update_version_entity,
        )
        return created_update_version

    async def get_all_update_versions(self) -> list[UpdateVersion]:
        return await self.__update_version_repository.list()

    async def download_latest_update_archive(self) -> tuple[bytes, str]:
        update_version = await self.__update_version_repository.get_latest()
        if update_version is None:
            raise UpdateVersionNotFoundException()

        archive_bytes = await self._build_archive(update_version)
        filename = f"update_v{update_version.version_number}.zip"
        return archive_bytes, filename

    async def download_update_archive_by_version(self, version_number: int) -> tuple[bytes, str]:
        update_version = await self.__update_version_repository.get_by_version_number(version_number)
        if update_version is None:
            raise UpdateVersionNotFoundException()

        archive_bytes = await self._build_archive(update_version)
        filename = f"update_v{update_version.version_number}.zip"
        return archive_bytes, filename

    async def _build_archive(self, update_version: UpdateVersion) -> bytes:
        archive_buffer = BytesIO()
        used_archive_names: set[str] = set()

        with ZipFile(archive_buffer, mode="w", compression=ZIP_DEFLATED) as zip_file:
            info_content = self._build_info_file_content(update_version)
            zip_file.writestr("update-description.txt", info_content)

            for file_entity in update_version.files:
                download_result = await self.__s3_client.download_file(file_entity.s3_key)

                if not download_result.get("success"):
                    error_msg = download_result.get("error_msg", "Unknown S3 error")
                    if "not found" in error_msg.lower():
                        raise UpdateFileNotFoundException(file_entity.s3_key)
                    raise UpdateArchiveBuildException(error_msg)

                archive_name = self._build_flat_archive_name(
                    s3_key=file_entity.s3_key,
                    used_archive_names=used_archive_names,
                    position=file_entity.position,
                )

                zip_file.writestr(archive_name, download_result["result"])

        archive_buffer.seek(0)
        return archive_buffer.getvalue()

    @staticmethod
    def _build_info_file_content(update_version: UpdateVersion) -> str:
        lines = [
            f"Version: {update_version.version_number}",
            f"Created at: {update_version.created_at.isoformat()}",
            "",
            "Description:",
            update_version.description,
            "",
            "Files:",
        ]
        lines.extend([f"- {file_entity.s3_key}" for file_entity in update_version.files])
        return "\n".join(lines)

    @staticmethod
    def _build_flat_archive_name(
            s3_key: str,
            used_archive_names: set[str],
            position: int,
    ) -> str:
        normalized = PurePosixPath(s3_key.lstrip("/"))
        if ".." in normalized.parts:
            raise UpdateArchiveBuildException("Unsafe S3 key detected while building archive")

        file_name = normalized.name
        if not file_name:
            raise UpdateArchiveBuildException("S3 key must point to a file")

        candidate = file_name
        if candidate in used_archive_names:
            candidate = f"{position + 1}_{candidate}"

        duplicate_counter = 1
        while candidate in used_archive_names:
            duplicate_counter += 1
            candidate = f"{position + 1}_{duplicate_counter}_{file_name}"

        used_archive_names.add(candidate)
        return candidate