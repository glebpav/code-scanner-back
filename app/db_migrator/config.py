import os

class Config:

    DATABASE_URL = os.environ['DB_URL']
    ADMIN_PASSWORD: str = os.environ['ADMIN_PASSWORD']

