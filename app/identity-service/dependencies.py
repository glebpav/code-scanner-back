from typing import Annotated

from fastapi import Depends
from shared_lib.db.repositories.user.user_role_repository import UserRoleRepository
from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db.repositories.user.user_repository import UserRepository

from config import Config
from database import get_db_session
from service.token_service import TokenService
from service.user_service import UserService


async def get_config():
    return Config()


async def get_user_repository(session: Annotated[AsyncSession, Depends(get_db_session)]):
    return UserRepository(session)


async def get_user_service(
        config: Annotated[Config, Depends(get_config)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
):
    return UserService(
        config=config,
        user_repository=UserRepository(session),
        user_role_repository=UserRoleRepository(session)
    )


async def get_token_service():
    return TokenService()
