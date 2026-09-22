from app.domain.enums import SeatStatus


class DomainError(Exception):
    """Базовая ошибка бизнес-правил домена."""


class SeatUnavailableError(DomainError):
    def __init__(self, seat_id: int) -> None:
        self.seat_id = seat_id
        super().__init__(f"Место {seat_id} недоступно для бронирования")


class InvalidSeatStateError(DomainError):
    def __init__(
        self,
        *,
        seat_id: int,
        action: str,
        status: SeatStatus,
    ) -> None:
        super().__init__(
            f"Нельзя выполнить действие: '{action}' для места {seat_id} "
            f"в статусе {status.value}"
        )


class InvalidBookingStateError(DomainError):
    def __init__(self, booking_id: int, status: str) -> None:
        self.booking_id = booking_id
        self.status = status
        super().__init__(f"Бронь {booking_id} нельзя изменить в статусе {status}")


class BookingExpiredError(DomainError):
    def __init__(self, booking_id: int) -> None:
        self.booking_id = booking_id
        super().__init__(f"Срок брони {booking_id} истёк")
