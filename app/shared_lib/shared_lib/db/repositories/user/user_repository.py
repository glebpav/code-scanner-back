from math import ceil
from typing import Optional, Dict, Any, Tuple, List

from sqlalchemy import select, func, case, literal, cast, or_
from sqlalchemy import String, DateTime, Numeric, Integer
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from shared_lib.db import User
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
                joinedload(User.status),
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
                joinedload(User.status),
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
                joinedload(User.status),
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
            .options(selectinload(User.role), selectinload(User.status))
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

    async def get_count_with_status(self, status_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.status_id == status_id,
                User.is_deleted == False
            )
        )
        result = await self._db_session.execute(stmt)
        return result.scalar_one()


    async def list_paginated(self, page: int = 1, limit: int = 15):
        if page < 1:
            page = 1
        if limit < 1:
            limit = 15

        total_stmt = select(func.count()).select_from(User).where(User.is_deleted == False)
        total_result = await self._db_session.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(User)
            .options(joinedload(User.status), joinedload(User.role))
            .where(User.is_deleted == False)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self._db_session.execute(stmt)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": ceil(total / limit) if total else 1,
        }

    def _role_name_sq(self):
        return (
            select(cast(Role.name, String))
            .where(Role.id == User.role_id)
            .scalar_subquery()
        )

    def _status_name_sq(self):
        return (
            select(cast(Status.name, String))
            .where(Status.id == User.status_id)
            .scalar_subquery()
        )

    def _builds_count_sq(self):
        return (
            select(func.count(Build.id))
            .where(
                Build.user_uuid == User.id,
                Build.version_status.notin_(
                    [
                        VersionStatusEnum.CANCELED,
                        VersionStatusEnum.RUNNING
                    ]
                )
            )
            .scalar_subquery()
        )

    def _sort_expression(self, sort: Optional[str]) -> Tuple[Any, List[Any]]:

        role_name = func.coalesce(self._role_name_sq(), literal(""))
        status_name = func.coalesce(self._status_name_sq(), literal(""))
        role_plus_status = func.concat(role_name, literal(" "), status_name)

        name_expr = func.concat(
            func.coalesce(User.first_name, literal("")),
            literal(" "),
            func.coalesce(User.last_name, literal(""))
        )

        builds_count = self._builds_count_sq()

        sort_map: Dict[str, Any] = {
            "name": name_expr,
            "email": User.email,
            "company": User.company,
            "role": role_plus_status,
            "targets": User.targets,
            "builds_count": builds_count,
            "created_at": User.created_at,
        }

        expr = sort_map.get(sort or "created_at", User.created_at)

        searchable: List[Any] = [
            cast(name_expr, String),
            cast(User.email, String),
            cast(User.company, String),
            cast(role_plus_status, String),
            cast(User.targets, String),
            cast(builds_count, String),
            cast(User.created_at, String),
        ]

        return expr, searchable

    def _order_expression(self, expr, order: str):
        if hasattr(expr.type, "_type_affinity") and issubclass(expr.type._type_affinity, String):
            base = func.lower(expr)
        else:
            base = expr

        if order == "asc":
            return base.asc().nulls_last()
        return base.desc().nulls_last()

    async def list_paginated_sorted_searched(
        self,
        page: int = 1,
        limit: int = 15,
        sort: Optional[str] = None,
        order: str = "desc",
        search: Optional[str] = None,
    ) -> Dict[str, Any]:

        page = max(page, 1)
        limit = max(limit, 1)

        sort_expr, searchable_exprs = self._sort_expression(sort)

        def _order_expr(expr, order):
            if hasattr(expr.type, "_type_affinity") and issubclass(expr.type._type_affinity, String):
                base = func.lower(expr)
            else:
                base = expr
            return base.asc().nulls_last() if order == "asc" else base.desc().nulls_last()

        filters = [User.is_deleted == False]

        if search:
            pat = f"%{search}%"
            or_clauses = [cast(expr, String).ilike(pat) for expr in searchable_exprs]
            filters.append(or_(*or_clauses))

        total_stmt = select(func.count()).select_from(User).where(*filters)
        total = (await self._db_session.execute(total_stmt)).scalar_one()

        pages = ceil(total / limit) if total > 0 else 0
        current_page = 1 if total == 0 else min(page, max(1, pages))

        stmt: Select = (
            select(User)
            .options(
                selectinload(User.status),
                selectinload(User.role),
            )
            .where(*filters)
            .order_by(
                _order_expr(sort_expr, order),
                User.id.asc()
            )
            .offset((current_page - 1) * limit)
            .limit(limit)
        )

        result = await self._db_session.execute(stmt)
        items = list(result.scalars().all())

        return {
            "items": items,
            "page": current_page,
            "limit": limit,
            "total": total,
            "pages": pages,
        }
