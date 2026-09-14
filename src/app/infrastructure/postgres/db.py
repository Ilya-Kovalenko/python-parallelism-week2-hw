from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import PostgresConfig


from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.repositories import EventRepo


@dataclass(frozen=True, slots=True)
class UnitOfWork:
    event_repo: EventRepo


class DatabaseManager:
    def __init__(self, config: PostgresConfig) -> None:
        self._engine: AsyncEngine = create_async_engine(
            config.url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:  # TODO: убрать если не нужно. Здесь просто создаём сессию, за коммит отвечает вызывающий код
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[UnitOfWork]:  # TODO: а тут конкретная транзакция и полный её откат при ошибке
        async with self._session_factory.begin() as session:
            yield UnitOfWork(
                event_repo=EventRepo(session),
            )

    async def close(self) -> None:
        await self._engine.dispose()
