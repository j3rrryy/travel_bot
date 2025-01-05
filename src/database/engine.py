from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import load_config


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    config = load_config()
    postgres_url = URL.create(
        drivername=config.postgres.driver,
        username=config.postgres.user,
        password=config.postgres.password,
        host=config.postgres.host,
        port=config.postgres.port,
        database=config.postgres.database,
    )

    async_engine = create_async_engine(url=postgres_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(bind=async_engine, class_=AsyncSession)
    return sessionmaker
