from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from database import get_db_session
from service.update_service import UpdateService
from service.user_token_auth_service import UserTokenAuthService
from shared_lib.db.repositories.update_version.update_version_repository import UpdateVersionRepository
from shared_lib.db.repositories.user_token.user_token_repository import UserTokenRepository
from shared_lib.s3 import S3Client


async def get_config():
    return Config()


async def get_update_version_repository(
        session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UpdateVersionRepository:
    return UpdateVersionRepository(session)


async def get_user_token_repository(
        session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserTokenRepository:
    return UserTokenRepository(session)


async def get_s3_client(
        config: Annotated[Config, Depends(get_config)],
) -> S3Client:
    return S3Client(
        access_key=config.OBJECT_STORAGE_ACCESS_KEY,
        secret_key=config.OBJECT_STORAGE_SECRET_KEY,
        endpoint_url=config.OBJECT_STORAGE_ENDPOINT_URL,
        bucket_name=config.OBJECT_STORAGE_BUCKET_NAME,
        region_name=config.OBJECT_STORAGE_REGION_NAME,
        verify_tls=config.OBJECT_STORAGE_VERIFY_TLS,
        force_path_style=config.OBJECT_STORAGE_FORCE_PATH_STYLE,
    )


async def get_update_service(
        config: Annotated[Config, Depends(get_config)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
        s3_client: Annotated[S3Client, Depends(get_s3_client)],
) -> UpdateService:
    return UpdateService(
        config=config,
        update_version_repository=UpdateVersionRepository(session),
        s3_client=s3_client,
    )


async def get_user_token_auth_service(
        config: Annotated[Config, Depends(get_config)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserTokenAuthService:
    return UserTokenAuthService(
        config=config,
        user_token_repository=UserTokenRepository(session),
    )
