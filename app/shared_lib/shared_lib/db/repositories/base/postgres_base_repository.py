from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

ModelType = TypeVar("ModelType")


class PostgresBaseRepository(Generic[ModelType]):
    def __init__(self, db_session: AsyncSession):
        if type(self) is PostgresBaseRepository:
            raise RuntimeError("Cannot instantiate abstract class 'BaseRepository'")
        self._db_session = db_session
        self.__model = self._get_model()

    @abstractmethod
    def _get_model(self) -> type[ModelType]:
        """ Critically important to implement this method in child classes """
        pass

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        stmt = select(self.__model).where(self.__model.id == id)
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> list[ModelType]:
        stmt = select(self.__model)
        result = await self._db_session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        self._db_session.add(obj)
        await self._db_session.flush()
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        if obj not in self._db_session:
            self._db_session.add(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self._db_session.delete(obj)

    async def commit(self):
        await self._db_session.commit()

    async def flush(self):
        await self._db_session.flush()
