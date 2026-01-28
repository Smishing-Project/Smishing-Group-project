from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings

Base = declarative_base()

engine: AsyncEngine = create_async_engine(
    settings.database_url, pool_pre_ping=True, echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def init_db():
    from app.db import models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def create_tables():
    await init_db()


async def get_db():
    if not getattr(get_db, "_initialized", False):
        await init_db()
        setattr(get_db, "_initialized", True)
    async with AsyncSessionLocal() as session:
        yield session
