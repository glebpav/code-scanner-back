from pydantic import BaseModel


class TokenWithRoleResponse(BaseModel):
    access_token: str
    refresh_token: str
    role: str
