from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import SeatStatus
from app.domain.exceptions import SeatUnavailableError, InvalidSeatStateError


@dataclass
class EventSeat:
    id: int
    event_id: int
    seat_id: int
    price: int
    status: SeatStatus
    reserved_until: datetime | None
    booking_id: int | None

    def reserve(self, *, booking_id: int, until: datetime) -> None:
        if self.status is not SeatStatus.AVAILABLE:
            raise SeatUnavailableError(self.id)

        self.status = SeatStatus.RESERVED
        self.booking_id = booking_id
        self.reserved_until = until

    def release(self, *, booking_id: int) -> None:
        if self.status is SeatStatus.SOLD:
            raise ValueError("Проданное место нельзя освободить")

        if self.status is not SeatStatus.RESERVED:
            raise InvalidSeatStateError(
                seat_id=self.id,
                action="release",
                status=self.status,
            )

        if self.booking_id != booking_id:
            raise SeatUnavailableError(self.id)

        self.status = SeatStatus.AVAILABLE
        self.booking_id = None
        self.reserved_until = None

    def sell(self, *, booking_id: int) -> None:
        if self.status is not SeatStatus.RESERVED:
            raise SeatUnavailableError(self.id)

        if self.booking_id != booking_id:
            raise SeatUnavailableError(self.id)

        self.status = SeatStatus.SOLD
        self.reserved_until = None
