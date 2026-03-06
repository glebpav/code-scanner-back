from sqlalchemy.orm import DeclarativeBase
from typing import Any, Dict, Type, TypeVar, Optional

T = TypeVar("T", bound="MongoAbstractEntity")


class PostgresAbstractEntity(DeclarativeBase):
    pass
