from commons.constants import DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator


class Base(DeclarativeBase):
    pass


class DatabaseConnection:
    _instance = None

    def __new__(
        cls,
        database_url=DATABASE_URL,
    ):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, database_url=DATABASE_URL):
        if getattr(self, "_initialized", False):
            return
        if not database_url:
            raise ValueError(
                "DATABASE_URL is not configured. Set it in your environment or .env file."
            )

        self.database_url = database_url
        self.engine = create_async_engine(self.database_url)
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )
        self.Base = Base
        self._initialized = True

    async def connect(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    async def disconnect(self):
        await self.engine.dispose()

    def get_base(self) -> type[Base]:
        return self.Base
