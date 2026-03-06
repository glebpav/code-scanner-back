from math import ceil
from typing import Optional, Dict, Any, Tuple, List

from sqlalchemy import select, func, case, literal, cast, or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db.models.user import User, Role
from shared_lib.db.repositories.base.postgres_base_repository import PostgresBaseRepository

Order = str  # "asc" | "desc"


class UserRepository(PostgresBaseRepository[User]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)

    def _get_model(self) -> type[User]:
        return User

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(
                joinedload(User.role)
            )
            .where(
                User.id == user_id,
                User.is_deleted == False
            )
        )
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> List[User]:
        stmt = (
            select(User)
            .options(
                joinedload(User.role)
            )
            .where(User.is_deleted == False)
        )
        result = await self._db_session.execute(stmt)
        return list(result.scalars().all())

    async def update_user(self, user: User, update_data: dict) -> None:
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.commit()

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = (
            select(User)
            .options(
                joinedload(User.role)
            )
            .where(
                User.email == email,
                User.is_deleted == False
            )
        )
        result = await self._db_session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self._db_session.add(user)
        await self.commit()
        await self._db_session.refresh(user)

        refreshed_result = await self._db_session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user.id)
        )

        fully_loaded_user = refreshed_result.scalar_one()
        return fully_loaded_user

    async def update_user_target_by_id(self, user_id, target: int) -> Optional[User]:

        user = await self.get_by_id(user_id=user_id)

        if not user:
            return None

        user.targets = target

        self._db_session.add(user)
        await self.flush()
        await self.commit()
        await self._db_session.refresh(user)
        return user

    async def soft_delete_by_id(self, user_id: str) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        if user.is_deleted:
            return True

        user.is_deleted = True
        self._db_session.add(user)
        await self.commit()
        return True
