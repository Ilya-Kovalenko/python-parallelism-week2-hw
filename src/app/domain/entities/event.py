from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    id: int
    organizer_id: int
    location_id: int
    title: str
    description: str | None
    category: str
    starts_at: datetime
    base_price: int
