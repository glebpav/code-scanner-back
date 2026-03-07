from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class CreateUpdateVersionRequest(BaseModel):
    description: Annotated[str, Field(min_length=1, max_length=5000)]
    file_keys: Annotated[list[str], Field(min_length=1, max_length=500)]

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Description must not be empty")
        return normalized

    @field_validator("file_keys")
    @classmethod
    def validate_file_keys(cls, values: list[str]) -> list[str]:
        normalized_values: list[str] = []
        seen: set[str] = set()

        for raw_key in values:
            key = raw_key.strip()
            if not key:
                raise ValueError("File key must not be empty")

            path = PurePosixPath(key)
            if key.startswith("/") or ".." in path.parts:
                raise ValueError("File key must be a safe relative S3 path")

            if key not in seen:
                seen.add(key)
                normalized_values.append(key)

        if not normalized_values:
            raise ValueError("At least one file key is required")

        return normalized_values


class UpdateVersionResponse(BaseModel):
    version_number: int
    description: str
    created_at: datetime
    file_keys: list[str]