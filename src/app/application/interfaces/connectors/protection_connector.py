from abc import ABC, abstractmethod
from datetime import datetime
from app.application.dto import Protection


class ProtectionConnector(ABC):
    @abstractmethod
    async def get_protection_availability(
        self,
        booking_id: int,
        ticket_amount: int,
        event_category: str,
        event_starts_at: datetime,
    ) -> Protection: ...
