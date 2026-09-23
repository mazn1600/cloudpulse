from collections.abc import AsyncIterator
from typing import Annotated, Literal

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import get_settings


DatabaseStatus = Literal["up", "down"]

engine = create_async_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_database_status() -> DatabaseStatus:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "up"
    except (SQLAlchemyError, OSError):
        return "down"


DatabaseStatusDep = Annotated[DatabaseStatus, Depends(get_database_status)]
