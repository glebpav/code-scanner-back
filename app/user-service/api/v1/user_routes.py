from typing import List

from fastapi import APIRouter, Depends

from dependencies import get_user_service
from scheme.user_scheme import UserResponse
from service.user_service import UserService

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get(
    "/all",
    response_model=List[UserResponse],
)
async def get_all_users(
        user_service: UserService = Depends(get_user_service),
) -> List[UserResponse]:

    # TODO: check user role -> if this user is not admin throw exception

    user_entity_list = await user_service.get_users()
    return [
        UserResponse.from_entity(user_entity)
        for user_entity in user_entity_list
    ]
