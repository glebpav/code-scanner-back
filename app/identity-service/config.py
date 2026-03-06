import os


class Config:

    ALLOW_ALL_ORIGINS: bool = bool(os.getenv("ALLOW_ALL_ORIGINS", False))

    JWT_SECRET: str = os.getenv("JWT_SECRET", "secret_key")
    REFRESH_SECRET: str = os.getenv("REFRESH_SECRET", "refresh_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    DATABASE_URL: str = os.environ['DB_ASYNC_URL']
