from typing import Optional

from pydantic import BaseModel
from shared_lib.db.models.user import User


class UserResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: str
    position: Optional[str]
    company: Optional[str]

    @staticmethod
    def from_entity(entity: User) -> "UserResponse":
        return UserResponse(
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            role=entity.role.name,
            position=entity.position,
            company=entity.company,
        )