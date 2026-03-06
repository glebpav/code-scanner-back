from fastapi import HTTPException


class MissingAuthorizationHeaderException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Missing or invalid Authorization header")


class AuthorizationTokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Authorization token is expired")


class InvalidAuthorizationTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Authorization token is invalid")
