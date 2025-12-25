from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from app.core.config import databaseconfig
from typing import AsyncGenerator




# Create async engine
engine = create_async_engine(
    url=databaseconfig.database_url(),
    echo=False,             
    future=True,
    pool_pre_ping=True,   
)

# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# DEPENDENCY: get_session()
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes.
    Creates a database session for each request,
    yields it to the route, and ensures cleanup afterward.
    """
    async with AsyncSessionLocal() as session:
        yield session



        


# INITIALIZATION: init_db()
async def init_db() -> None:
    """
    Initialize the database and create all tables defined in models.
    Run this on startup or manually in an initialization script.
    """
    from app.db import models  # Import models here to register metadata

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("Database tables created successfully.")
