from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateUserTokenRequest(BaseModel):
    first_name: str
    last_name: str

class CreateUserTokenResponse(BaseModel):
    token_id: UUID
    first_name: str
    last_name: str
    created_at: datetime
    is_active: bool
    token: str

class DeactivateUserTokenRequest(BaseModel):
    token_id: UUID
