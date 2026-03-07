from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db.models.user_token import UserToken
from shared_lib.db.repositories.base.postgres_base_repository import PostgresBaseRepository


class UserTokenRepository(PostgresBaseRepository[UserToken]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)

    def _get_model(self) -> type[UserToken]:
        return UserToken

    async def create(self, user_token: UserToken) -> UserToken:
        self._db_session.add(user_token)
        await self.commit()
        await self._db_session.refresh(user_token)
        return user_token

    async def get_by_id(self, token_id: UUID) -> Optional[UserToken]:
        stmt = select(UserToken).where(UserToken.id == token_id)
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> List[UserToken]:
        stmt = select(UserToken)
        result = await self._db_session.execute(stmt)
        return list(result.scalars().all())

    async def set_is_active(self, token_id: UUID, is_active: bool) -> Optional[UserToken]:
        user_token = await self.get_by_id(token_id=token_id)

        if not user_token:
            return None

        user_token.is_active = is_active

        self._db_session.add(user_token)
        await self.flush()
        await self.commit()
        await self._db_session.refresh(user_token)
        return user_token