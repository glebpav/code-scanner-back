import asyncio
from abc import ABC
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db.repositories.base.postgres_base_repository import PostgresBaseRepository, ModelType


class CachedBaseRepository(ABC, PostgresBaseRepository[ModelType]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.__cache: Optional[dict] = None
        self.__lock = asyncio.Lock()

    async def _get_cache(self) -> dict:
        if self.__cache is None:
            async with self.__lock:
                if self.__cache is None:
                    items = await super().list()
                    self.__cache = {item.id: item for item in items}
        return self.__cache

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        cache = await self._get_cache()
        return cache.get(id)

    async def list(self) -> list[ModelType]:
        cache = await self._get_cache()
        return list(cache.values())

    async def create(self, obj: ModelType) -> ModelType:
        self.__cache = None
        self._db_session.add(obj)
        await self._db_session.flush()
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        self.__cache = None
        self._db_session.add(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        self.__cache = None
        await self._db_session.delete(obj)
