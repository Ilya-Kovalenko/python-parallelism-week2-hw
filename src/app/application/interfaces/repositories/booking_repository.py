from datetime import datetime
from abc import ABC, abstractmethod

from app.domain.entities import Booking
from app.application.dto import SalesStats


class BookingRepository(ABC):
    @abstractmethod
    async def create_booking(
        self, event_id: int, user_id: int, amount: int, reserved_until: datetime
    ) -> Booking: ...

    @abstractmethod
    async def get_for_update(self, booking_id: int) -> Booking: ...

    @abstractmethod
    async def save_booking(self, booking: Booking) -> None: ...

    @abstractmethod
    async def get_sales_stats(self, event_id: int) -> SalesStats: ...
