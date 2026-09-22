from typing import Sequence


class ApplicationError(Exception):
    """Базовая ошибка сценариев приложения."""


class SeatReservationInProgressError(ApplicationError):
    """Место в данный момент обрабатывается другим бронированием."""


class ExternalServiceUnavailableError(ApplicationError):
    """Внешний сервис не ответил или вернул ошибку после всех попыток."""

    service_name = "external"

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Сервис {self.service_name} недоступен: {reason}")


class PaymentServiceUnavailableError(ExternalServiceUnavailableError):
    service_name = "payment"


class ProtectionServiceUnavailableError(ExternalServiceUnavailableError):
    service_name = "protection"


class EventNotFoundError(ApplicationError):
    def __init__(self, event_id: int) -> None:
        self.event_id = event_id
        super().__init__(f"Мероприятие {event_id} не найдено")


class BookingNotFoundError(ApplicationError):
    def __init__(self, booking_id: int) -> None:
        self.booking_id = booking_id
        super().__init__(f"Бронь {booking_id} не найдена")


class SeatNotFoundError(ApplicationError):
    def __init__(self, event_id: int, seat_ids: Sequence[int]) -> None:
        self.event_id = event_id
        self.seat_ids = list(seat_ids)
        super().__init__(f"Места {self.seat_ids} не найдены на мероприятии {event_id}")


class EventAccessDeniedError(ApplicationError):
    def __init__(self, event_id: int, organizer_id: int) -> None:
        self.event_id = event_id
        self.organizer_id = organizer_id
        super().__init__(
            f"Пользователь {organizer_id} не является организатором мероприятия {event_id}"
        )
