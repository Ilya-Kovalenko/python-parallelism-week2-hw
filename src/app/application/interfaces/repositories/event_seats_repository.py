from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.event_seat import EventSeat
from app.application.dto import OccupancyStats


class EventSeatsRepository(ABC):
    @abstractmethod
    async def get_seats_for_reserve(
        self, event_id: int, seat_ids: Sequence[int]
    ) -> Sequence[EventSeat]: ...

    @abstractmethod
    async def save_many(self, seats: Sequence[EventSeat]) -> None: ...

    @abstractmethod
    async def get_occupancy_stats(self, event_id: int) -> OccupancyStats: ...
