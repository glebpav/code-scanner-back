import datetime
from typing import List

from shared_lib.db.models.user_token import UserToken
from shared_lib.db.repositories.user_token.user_token_repository import UserTokenRepository

from config import Config
from scheme.user_token_scheme import CreateUserTokenRequest, DeactivateUserTokenRequest


class UserTokenService:
    def __init__(
            self,
            config: Config,
            user_token_repository: UserTokenRepository
    ):
        self.__config = config
        self.__user_token_repository = user_token_repository

    async def create_user_token(
            self,
            create_user_token_request: CreateUserTokenRequest
    ) -> UserToken:

        user_token_entity = UserToken(
            first_name=create_user_token_request.first_name,
            last_name=create_user_token_request.last_name,
            created_at=datetime.now(),
            is_active=True,
        )

        created_user_token = await self.__user_token_repository.create(
            user_token=user_token_entity
        )

        return created_user_token

    async def deactivate_user_token(
            self,
            deactivate_user_token_request: DeactivateUserTokenRequest
    ) -> None:

        # TODO: check if this token exists and is already deactivated

        _ = await self.__user_token_repository.set_is_active(
            token_id=deactivate_user_token_request.token_id,
            is_active=False
        )

    async def get_all_user_tokens(self) -> List[UserToken]:
        return await self.__user_token_repository.list()

