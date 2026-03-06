from typing import List
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session


class DataBase:
    """
    SQLAlchemy python wrapper.

    To add objects use methods add and add_all.
    To query db get db session with "session" property in context manager:

        with db.session as session:
            for user in session.query(User).all():
                print(user)
    """

    def __init__(self, db_url: str, is_db_async: bool = False):
        self.__is_db_async = is_db_async
        self.__db_url = db_url

        if is_db_async:
            engine = create_async_engine(db_url, echo=True)
            self.async_session = async_sessionmaker(
                engine,
                expire_on_commit=False
            )
        else:
            self.engine = create_engine(db_url)

    async def get_async_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session


    @property
    @contextmanager
    def session(self):
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add(self, obj):
        with Session(self.engine) as session, session.begin():
            session.add(obj)

    def add_all(self, objs: List):
        with Session(self.engine) as session, session.begin():
            session.add_all(objs)
