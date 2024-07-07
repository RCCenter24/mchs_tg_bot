from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base


DBURL='postgresql+asyncpg://rejoller:9205@localhost:5432/mchs_tg'


engine = create_async_engine(DBURL, echo=False)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)