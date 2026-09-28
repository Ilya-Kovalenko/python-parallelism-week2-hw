from dataclasses import dataclass
from datetime import datetime, UTC

from app.domain.enums import BookingStatus
from app.domain.exceptions import BookingExpiredError, InvalidBookingStateError


@dataclass
class Booking:
    id: int
    event_id: int
    user_id: int
    amount: int
    payment_commission: int
    protection_price: int | None
    with_protection: bool
    status: BookingStatus
    reserved_until: datetime

    def apply_pricing(
        self,
        amount: int,
        payment_commission: int,
        protection_price: int | None,
        with_protection: bool,
    ) -> None:
        if self.status != BookingStatus.PREPARING:
            raise InvalidBookingStateError(booking_id=self.id, status=self.status)

        if self.reserved_until <= datetime.now(UTC):
            raise BookingExpiredError(booking_id=self.id)

        if amount < 0:
            raise ValueError("Сумма бронирования не может быть негативной")

        if payment_commission < 0:
            raise ValueError("Комиссия не может быть негативной")

        if with_protection and protection_price is None:
            raise ValueError("protection_price обязателен когда with_protection=True")

        if not with_protection:
            protection_price = None

        self.amount = amount
        self.payment_commission = payment_commission
        self.protection_price = protection_price
        self.with_protection = with_protection
        self.status = BookingStatus.PENDING_PAYMENT

    def mark_paid(self, *, now: datetime) -> None:
        if self.status is not BookingStatus.PENDING_PAYMENT:
            raise InvalidBookingStateError(booking_id=self.id, status=self.status)

        if self.reserved_until <= now:
            raise BookingExpiredError(booking_id=self.id)

        self.status = BookingStatus.PAID

    def cancel(self) -> None:
        if self.status is BookingStatus.PAID:
            raise ValueError("Оплаченную бронь нельзя отменить этим способом")

        self.status = BookingStatus.CANCELLED

    def expire(self, *, now: datetime) -> bool:
        if self.status is not BookingStatus.PENDING_PAYMENT:
            return False

        if self.reserved_until > now:
            return False

        self.status = BookingStatus.EXPIRED
        return True
