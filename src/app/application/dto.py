from dataclasses import dataclass
from datetime import datetime
from typing import Sequence
from app.domain.entities import Booking, Event, EventSeat


@dataclass(frozen=True, slots=True)
class Payment:
    commission: int
    total: int
    payment_methods: list[str]
    expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class Protection:
    available: bool
    price: int
    covered_amount: int


@dataclass(frozen=True, slots=True)
class Checkout:
    booking: Booking
    seats: Sequence[EventSeat]
    event: Event
    protection: Protection | None
    payment: Payment


@dataclass(frozen=True, slots=True)
class SalesStats:
    paid_orders: int
    revenue: int
    average_order: int


@dataclass(frozen=True, slots=True)
class OccupancyStats:
    total: int
    available: int
    reserved: int
    sold: int
    occupancy_percent: float


@dataclass(frozen=True, slots=True)
class EventDashboard:
    event: Event
    sales: SalesStats
    occupancy: OccupancyStats
