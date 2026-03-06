from passlib.context import CryptContext
from shared_lib.db.models.user import User, UserRole
from shared_lib.db.repositories.user.user_repository import UserRepository
from shared_lib.db.repositories.user.user_role_repository import UserRoleRepository

from config import Config
from exception.auth_exception import UserNotFoundException, UserAlreadyExistsException, WrongPasswordException
from schemes.user_schema import UserResponse, CreateUserRequest, LoginUserRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(
            self,
            config: Config,
            user_repository: UserRepository,
            user_role_repository: UserRoleRepository,
    ):
        self.__config = config
        self.__user_repository = user_repository
        self.__user_role_repository = user_role_repository

    async def get_users(self) -> list[UserResponse]:
        users = await self.__user_repository.list()
        return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id) -> User:
        user = await self.__user_repository.get_by_id(
            user_id=user_id
        )

        if user is None:
            raise UserNotFoundException()

        return user

    async def create_user(self, user_data: CreateUserRequest) -> User:

        found_user = await self.__user_repository.get_by_email(user_data.email)
        if found_user is not None:
            raise UserAlreadyExistsException()

        hashed_password = pwd_context.hash(user_data.password)

        role = await self.__user_role_repository.get_by_name(UserRole.USER.value)

        user_entity = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            company=user_data.company,
            position=user_data.position,
            role_id=role.id,
            is_deleted=False
        )

        created_user = await self.__user_repository.create(user_entity)

        return created_user

    async def check_password(self, user_data: LoginUserRequest) -> User:

        found_user = await self.__user_repository.get_by_email(user_data.email)
        if found_user is None:
            raise UserNotFoundException()

        if not pwd_context.verify(user_data.password, found_user.hashed_password):
            raise WrongPasswordException()

        return found_user
