import uuid

from pydantic import BaseModel, model_validator, field_validator, Field
from typing import Optional, Annotated

import re


class CreateUserRequest(BaseModel):
    first_name: Optional[Annotated[str, Field(max_length=64)]] = None
    last_name: Optional[Annotated[str, Field(max_length=64)]] = None
    email: Annotated[str, Field(max_length=254)]
    position: Optional[Annotated[str, Field(max_length=128)]] = None
    company: Annotated[str, Field(max_length=128)]
    password: Annotated[str, Field(max_length=64)]

    @model_validator(mode='after')
    def check_name(self):
        if not self.first_name and not self.last_name:
            raise ValueError('Either first_name or last_name is required')
        return self

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        if len(value) > 254:
            raise ValueError('Email must be at most 254 characters long')

        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")

        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Za-z]', value):
            raise ValueError('Password must contain at least one letter')

        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')

        if not re.search(r'[@#$%^&+=!_⸺-]', value):
            raise ValueError('Password must contain at least one special character (@, #, $, %, ^, &, +, =, !, _, -, ⸺)')

        return value


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    company: Optional[str]
    position: Optional[str]
    research_area: Optional[str]
    role: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class LoginUserRequest(BaseModel):
    email: str
    password: str
