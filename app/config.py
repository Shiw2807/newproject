import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    database_url: str = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5433/perms")
    async_database_url: str = os.environ.get("ASYNC_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/perms")
    external_roles_url: str = os.environ.get("EXTERNAL_ROLES_URL", "http://localhost:9999/mock-roles")

settings = Settings()
