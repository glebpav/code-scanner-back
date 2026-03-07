from typing import List
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette import status

from dependencies import get_user_token_service, get_config, get_decoder_service
from scheme.user_token_scheme import CreateUserTokenRequest, CreateUserTokenResponse, DeactivateUserTokenRequest
from service.decoder_service import DecoderService
from service.user_token_service import UserTokenService

router = APIRouter(prefix="/user-token", tags=["UserToken"])


@router.post(
    "/create",
    response_model=CreateUserTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_token(
        create_user_token_request: CreateUserTokenRequest,
        decoder_service: DecoderService = Depends(get_decoder_service),
        user_token_service: UserTokenService = Depends(get_user_token_service),
) -> CreateUserTokenResponse:
    # TODO: check user role -> if this user is not admin throw exception

    user_token_entity = await user_token_service.create_user_token(
        create_user_token_request=create_user_token_request
    )

    token = decoder_service.create_signed_token(
        user_token_entity=user_token_entity
    )

    return CreateUserTokenResponse(
        token_id=user_token_entity.id,
        first_name=user_token_entity.first_name,
        last_name=user_token_entity.last_name,
        created_at=user_token_entity.created_at,
        is_active=user_token_entity.is_active,
        token=token
    )


@router.delete(
    "/deactivate/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_token(
        token_id: UUID,
        user_token_service: UserTokenService = Depends(get_user_token_service),
) -> None:
    # TODO: check user role -> if this user is not admin throw exception

    await user_token_service.deactivate_user_token(
        deactivate_user_token_request=DeactivateUserTokenRequest(
            token_id=token_id
        )
    )


@router.get(
    "/all",
    response_model=List[CreateUserTokenResponse],
)
async def get_user_tokens(
        decoder_service: DecoderService = Depends(get_decoder_service),
        user_token_service: UserTokenService = Depends(get_user_token_service),
) -> List[CreateUserTokenResponse]:
    # TODO: check user role -> if this user is not admin throw exception

    user_token_list = await user_token_service.get_all_user_tokens()

    return [
        CreateUserTokenResponse(
            token_id=user_token_entity.id,
            first_name=user_token_entity.first_name,
            last_name=user_token_entity.last_name,
            created_at=user_token_entity.created_at,
            is_active=user_token_entity.is_active,
            token=decoder_service.create_signed_token(
                user_token_entity=user_token_entity
            )
        )
        for user_token_entity in user_token_list
    ]
