import os


class Config:
    ALLOW_ALL_ORIGINS: bool = bool(os.getenv("ALLOW_ALL_ORIGINS", False))
    JWT_SECRET: str = os.environ["JWT_SECRET"]
    DATABASE_URL: str = os.environ['DB_ASYNC_URL']
    USER_TOKEN_SECRET: str = os.environ["USER_TOKEN_SECRET"]