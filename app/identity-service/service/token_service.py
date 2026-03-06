import uuid
from datetime import datetime, timedelta
from typing import Union

import jwt
from shared_lib.auth import InvalidAuthorizationTokenException, decode_validate_access_token

from schemes.token_schema import TokenResponse, AccessTokenResponse


class TokenService:

    @staticmethod
    def __generate_token(user_id: Union[uuid.UUID, str], expire_time_minutes, secrete) -> str:
        return jwt.encode({
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(minutes=expire_time_minutes)
        }, secrete, algorithm='HS256')

    @staticmethod
    def generate_tokens(
            user_id: uuid,
            refresh_secret: str,
            access_secret: str,
            access_expire_minutes: int,
            refresh_expire_minutes: int
    ) -> TokenResponse:
        return TokenResponse(
            access_token=TokenService.__generate_token(
                user_id,
                access_expire_minutes,
                access_secret
            ),
            refresh_token=TokenService.__generate_token(
                user_id,
                refresh_expire_minutes,
                refresh_secret
            ),
        )

    @staticmethod
    def generate_new_access_token(
            previous_token_payload: dict,
            expire_time_minutes: int,
            secrete: str
    ) -> AccessTokenResponse:

        if "user_id" not in previous_token_payload:
            raise InvalidAuthorizationTokenException()

        user_id = previous_token_payload.get("user_id")

        access_token = TokenService.__generate_token(
            user_id,
            expire_time_minutes,
            secrete
        )

        return AccessTokenResponse(access_token=access_token)

    @staticmethod
    def create_service_token(
            client_id: str,
            scopes: list[str],
            access_expire_minutes: int,
            secrete: str
    ):
        expire = datetime.utcnow() + timedelta(
            minutes=access_expire_minutes
        )

        payload = {
            "sub": client_id,
            "scope": scopes,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "idp"
        }

        token = jwt.encode(
            payload,
            secrete,
            algorithm='HS256'
        )

        return token

    @staticmethod
    def decode_and_validate(token: str, secret: str) -> dict:
        return decode_validate_access_token(token, secret)


