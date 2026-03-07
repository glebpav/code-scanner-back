from typing import Annotated

from fastapi import Depends
from shared_lib.db.repositories.user.user_role_repository import UserRoleRepository
from shared_lib.db.repositories.user_token.user_token_repository import UserTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db.repositories.user.user_repository import UserRepository

from config import Config
from database import get_db_session
from service.decoder_service import DecoderService
from service.user_token_service import UserTokenService


async def get_config():
    return Config()


async def get_user_token_repository(
        session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UserTokenRepository:
    return UserTokenRepository(session)


async def get_user_token_service(
        config: Annotated[Config, Depends(get_config)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return UserTokenService(
        config=config,
        user_token_repository=UserTokenRepository(session)
    )


async def get_decoder_service(
        config: Annotated[Config, Depends(get_config)],
):
    return DecoderService(
        config=config
    )
