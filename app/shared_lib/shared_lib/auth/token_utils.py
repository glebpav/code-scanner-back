from fastapi import Request

import jwt

from .token_exceptions import (MissingAuthorizationHeaderException,
                               AuthorizationTokenExpiredException,
                               InvalidAuthorizationTokenException)


def get_token_from_request(request: Request) -> str:

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    raise MissingAuthorizationHeaderException()


def decode_validate_access_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload

    except jwt.ExpiredSignatureError:
        raise AuthorizationTokenExpiredException()

    except jwt.InvalidTokenError:
        raise InvalidAuthorizationTokenException()


def fetch_payload_from_request(request: Request, secret: str) -> dict:
    token = get_token_from_request(request)
    return decode_validate_access_token(token, secret)
