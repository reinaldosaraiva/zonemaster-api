from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from .base import Base

def create_async_db_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

def create_async_session_factory():
    engine = create_async_db_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

# Create globals
async_engine = None
AsyncSessionLocal = None

def init_db():
    global async_engine, AsyncSessionLocal
    async_engine = create_async_db_engine()
    AsyncSessionLocal = create_async_session_factory()

async def get_db() -> AsyncSession:
    if AsyncSessionLocal is None:
        init_db()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()