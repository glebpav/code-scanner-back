from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared_lib.db.models.update_version import UpdateVersion
from shared_lib.db.repositories.base.postgres_base_repository import PostgresBaseRepository


class UpdateVersionRepository(PostgresBaseRepository[UpdateVersion]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)

    def _get_model(self) -> type[UpdateVersion]:
        return UpdateVersion

    async def create(self, update_version: UpdateVersion) -> UpdateVersion:
        self._db_session.add(update_version)
        await self.commit()
        created = await self.get_by_id(update_version.id)
        assert created is not None
        return created

    async def get_by_id(self, update_version_id: UUID) -> Optional[UpdateVersion]:
        stmt = (
            select(UpdateVersion)
            .options(selectinload(UpdateVersion.files))
            .where(UpdateVersion.id == update_version_id)
        )
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_version_number(self, version_number: int) -> Optional[UpdateVersion]:
        stmt = (
            select(UpdateVersion)
            .options(selectinload(UpdateVersion.files))
            .where(UpdateVersion.version_number == version_number)
        )
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest(self) -> Optional[UpdateVersion]:
        stmt = (
            select(UpdateVersion)
            .options(selectinload(UpdateVersion.files))
            .order_by(UpdateVersion.version_number.desc())
            .limit(1)
        )
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> list[UpdateVersion]:
        stmt = (
            select(UpdateVersion)
            .options(selectinload(UpdateVersion.files))
            .order_by(UpdateVersion.version_number.desc())
        )
        result = await self._db_session.execute(stmt)
        return list(result.scalars().all())