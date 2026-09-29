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
from app.application.interfaces.unit_of_work import DatabaseManager, UnitOfWork
from app.application.interfaces.repositories import (
    BookingRepository,
    EventRepository,
    EventSeatsRepository,
)
from app.infrastructure.postgres.repositories import (
    PostgresBookingRepository,
    PostgresEventRepository,
    PostgresEventSeatsRepository,
)


@dataclass(frozen=True, slots=True)
class SqlAlchemyUnitOfWork(UnitOfWork):
    booking_repository: BookingRepository
    event_repository: EventRepository
    event_seats_repository: EventSeatsRepository


class SqlAlchemyDatabaseManager(DatabaseManager):
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
    async def session(
        self,
    ) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def transaction(
        self,
    ) -> AsyncIterator[UnitOfWork]:
        async with self._session_factory.begin() as session:
            yield SqlAlchemyUnitOfWork(
                booking_repository=PostgresBookingRepository(session),
                event_repository=PostgresEventRepository(session),
                event_seats_repository=PostgresEventSeatsRepository(session),
            )

    async def close(self) -> None:
        await self._engine.dispose()
