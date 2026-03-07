import os


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    ALLOW_ALL_ORIGINS: bool = _get_bool_env("ALLOW_ALL_ORIGINS", False)
    DATABASE_URL: str = os.environ["DB_ASYNC_URL"]

    USER_TOKEN_SECRET: str = os.environ["USER_TOKEN_SECRET"]

    OBJECT_STORAGE_ACCESS_KEY: str = os.environ["OBJECT_STORAGE_ACCESS_KEY"]
    OBJECT_STORAGE_SECRET_KEY: str = os.environ["OBJECT_STORAGE_SECRET_KEY"]
    OBJECT_STORAGE_ENDPOINT_URL: str = os.environ["OBJECT_STORAGE_ENDPOINT_URL"]
    OBJECT_STORAGE_BUCKET_NAME: str = os.environ["OBJECT_STORAGE_BUCKET_NAME"]
    OBJECT_STORAGE_REGION_NAME: str = os.environ["OBJECT_STORAGE_REGION_NAME"]

    OBJECT_STORAGE_VERIFY_TLS: bool = _get_bool_env("OBJECT_STORAGE_VERIFY_TLS", True)

    OBJECT_STORAGE_FORCE_PATH_STYLE: bool = _get_bool_env("OBJECT_STORAGE_FORCE_PATH_STYLE", True)