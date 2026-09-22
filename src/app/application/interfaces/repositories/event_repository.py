from abc import ABC, abstractmethod

from app.domain.entities import Event


class EventRepository(ABC):
    @abstractmethod
    async def get_event(self, event_id: int) -> Event: ...
