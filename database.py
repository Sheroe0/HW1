from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import asyncio

#DATABASE_URL = "postgresql+asyncpg://USER:PASS@HOST:PORT/NAME"
DATABASE_URL = "postgresql+asyncpg://postgres:123tyklty@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#async def main():
#   await create_tables()
#asyncio.run(main())