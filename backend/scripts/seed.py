import asyncio

from sqlalchemy import func, select

from app.database import session_factory
from app.models import Deployment


async def seed() -> None:
    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(Deployment))
        if count == 0:
            session.add(
                Deployment(
                    version="v0.1.0",
                    environment="local",
                    status="successful",
                )
            )
            await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
