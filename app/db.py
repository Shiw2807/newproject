from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Sync engine and session (used by some repos)
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Async engine (used by other repos, intentionally mixed)
async_engine: AsyncEngine = create_async_engine(settings.async_database_url, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=None, autocommit=False, autoflush=False)
# NOTE: We purposely don't use SQLAlchemy AsyncSession class here to create some friction; some modules will use asyncpg directly.
