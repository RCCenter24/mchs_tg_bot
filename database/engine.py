from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.db_config import (user, password, host, port, database)


DBURL=f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'


engine = create_async_engine(DBURL, echo=False)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)