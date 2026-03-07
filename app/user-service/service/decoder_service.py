import datetime
from uuid import UUID

import jwt
from shared_lib.db.models.user_token import UserToken

from config import Config


class DecoderService:

    ALGORITHM = "HS256"

    def __init__(
            self,
            config: Config,
    ):
        self.__config = config

    def create_signed_token(
            self,
            user_token_entity: UserToken,
    ) -> str:
        payload = {
            "id": str(user_token_entity.id),
            "first_name": user_token_entity.first_name,
            "last_name": user_token_entity.last_name,
            "created_at": user_token_entity.created_at.isoformat(),
            "is_active": user_token_entity.is_active,
        }

        return jwt.encode(
            payload,
            self.__config.USER_TOKEN_SECRET,
            algorithm=self.ALGORITHM,
        )

    def decode_signed_token(
            self,
            token: str,
    ) -> UserToken:
        payload = jwt.decode(
            token,
            self.__config.USER_TOKEN_SECRET,
            algorithms=[self.ALGORITHM],
        )

        return UserToken(
            id=UUID(payload["id"]),
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            created_at=datetime.fromisoformat(payload["created_at"]),
            is_active=payload["is_active"],
        )