from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db.models.user import Role
from shared_lib.db.repositories.base.postgres_cached_base_repository import CachedBaseRepository


class UserRoleRepository(CachedBaseRepository[Role]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)

    def _get_model(self) -> type[Role]:
        return Role

    async def get_by_name(self, name: str) -> Optional[Role]:
        cache = await self._get_cache()
        for role in cache.values():
            if role.name.value == name:
                return role
        return None
