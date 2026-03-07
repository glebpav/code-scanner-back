from typing import List

from passlib.context import CryptContext
from shared_lib.db.models.user import User
from shared_lib.db.repositories.user.user_repository import UserRepository
from shared_lib.db.repositories.user.user_role_repository import UserRoleRepository

from config import Config
from scheme.user_scheme import UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(
            self,
            config: Config,
            user_repository: UserRepository,
    ):
        self.__config = config
        self.__user_repository = user_repository

    async def get_users(self) -> list[User]:
        return await self.__user_repository.list()
