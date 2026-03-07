from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import Config


DATABASE_URL = Config.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        yield session