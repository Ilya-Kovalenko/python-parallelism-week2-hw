from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.repositories import BookingRepository, EventRepository, EventSeatsRepository


class UnitOfWork(ABC):
    @property
    @abstractmethod
    def booking_repository(self) -> BookingRepository:
        ...

    @property
    @abstractmethod
    def event_repository(self) -> EventRepository:
        ...

    @property
    @abstractmethod
    def event_seats_repository(self) -> EventSeatsRepository:
        ...


class DatabaseManager(ABC):
    @abstractmethod
    def transaction(self) -> AbstractAsyncContextManager[UnitOfWork]:
        ...
