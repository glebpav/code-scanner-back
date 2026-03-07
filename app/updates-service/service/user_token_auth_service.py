import jwt
from shared_lib.db.repositories.user_token.user_token_repository import UserTokenRepository

from config import Config
from exception.update_exception import InvalidUserTokenException, InactiveUserTokenException


class UserTokenAuthService:
    ALGORITHM = "HS256"

    def __init__(
            self,
            config: Config,
            user_token_repository: UserTokenRepository,
    ):
        self.__config = config
        self.__user_token_repository = user_token_repository

    def decode_signed_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.__config.USER_TOKEN_SECRET,
                algorithms=[self.ALGORITHM],
            )
        except jwt.PyJWTError:
            raise InvalidUserTokenException()

    async def validate_active_user_token(self, token: str) -> None:
        payload = self.decode_signed_token(token)

        token_id = payload.get("id")
        if token_id is None:
            raise InvalidUserTokenException()

        found_token = await self.__user_token_repository.get_by_id(token_id)
        if found_token is None:
            raise InvalidUserTokenException()

        if not found_token.is_active:
            raise InactiveUserTokenException()