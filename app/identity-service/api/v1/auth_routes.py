from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Request, Cookie, Body, Form
from starlette import status

from config import Config
from dependencies import get_user_service, get_token_service
from schemes.common_shema import TokenWithRoleResponse
from schemes.token_schema import AccessTokenResponse
from schemes.user_schema import CreateUserRequest, LoginUserRequest
from service.token_service import TokenService
from service.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Users"])


@router.post(
    "/register",
    response_model=TokenWithRoleResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        user_data: CreateUserRequest,
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service)
):
    user = await user_service.create_user(user_data)

    tokens = token_service.generate_tokens(
        user_id=user.id,
        refresh_secret=Config.REFRESH_SECRET,
        access_secret=Config.JWT_SECRET,
        access_expire_minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_minutes=Config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
    )

    return TokenWithRoleResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        role=user.role.name
    )


@router.post(
    "/login",
    response_model=TokenWithRoleResponse,
    status_code=status.HTTP_200_OK
)
async def login(
        user_data: LoginUserRequest,
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service)
):
    found_user = await user_service.check_password(user_data)

    tokens = token_service.generate_tokens(
        user_id=found_user.id,
        refresh_secret=Config.REFRESH_SECRET,
        access_secret=Config.JWT_SECRET,
        access_expire_minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_minutes=Config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
    )

    return TokenWithRoleResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        role=found_user.role.name
    )


@router.post(
    '/refresh',
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK)
async def refresh_token(
        token_service: TokenService = Depends(get_token_service),
        user_service: UserService = Depends(get_user_service),
        refresh_token_body: Optional[dict] = Body(default=None),
):
    if refresh_token_body and "refresh_token" in refresh_token_body:
        refresh_token = refresh_token_body["refresh_token"]
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not provided")

    payload = token_service.decode_and_validate(
        refresh_token,
        Config.REFRESH_SECRET
    )

    assert payload['user_id'] is not None
    _ = user_service.get_user_by_id(user_id=payload['user_id'])

    new_token = token_service.generate_new_access_token(
        payload,
        Config.ACCESS_TOKEN_EXPIRE_MINUTES,
        Config.JWT_SECRET
    )

    return new_token
