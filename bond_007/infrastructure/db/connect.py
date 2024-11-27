from persistent.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_url = "/sqlite.db"

# функции для подключения к базе данных
def sqlite_connection() -> async_sessionmaker[AsyncSession]:

	engine = create_async_engine(f"sqlite+aiosqlite://{_url}", connect_args={"check_same_thread": False})

	return async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
