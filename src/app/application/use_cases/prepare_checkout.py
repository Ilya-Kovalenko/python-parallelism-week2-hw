import asyncio
from typing import Sequence

from app.application.exceptions import ProtectionServiceUnavailableError
from app.application.interfaces.unit_of_work import DatabaseManager
from app.application.interfaces.connectors.payment_connector import PaymentConnector
from app.application.interfaces.connectors.protection_connector import (
    ProtectionConnector,
)
from app.application.dto import Checkout, Protection
from datetime import datetime, UTC, timedelta

from app.domain.entities import Booking, Event
from app.domain.exceptions import InvalidBookingStateError


class PrepareCheckoutUseCase:
    def __init__(
        self,
        db: DatabaseManager,
        payment_connector: PaymentConnector,
        protection_connector: ProtectionConnector,
    ) -> None:
        self.db = db
        self.payment_connector = payment_connector
        self.protection_connector = protection_connector

    async def execute(
        self, event_id: int, seat_ids: Sequence[int], user_id: int
    ) -> Checkout:
        reserved_until = datetime.now(UTC) + timedelta(minutes=15)

        async with self.db.transaction() as db:
            seats = await db.event_seats_repository.get_seats_for_reserve(
                event_id=event_id, seat_ids=seat_ids
            )

            event = await db.event_repository.get_event(event_id=event_id)
            amount = sum(seat.price for seat in seats)

            booking = await db.booking_repository.create_booking(
                event_id=event_id,
                user_id=user_id,
                amount=amount,
                reserved_until=reserved_until,
            )

            for seat in seats:
                seat.reserve(booking_id=booking.id, until=reserved_until)

            await db.event_seats_repository.save_many(seats)
            reserved_ids = {seat.id for seat in seats}

        payment_task = asyncio.create_task(
            self.payment_connector.get_payment(
                booking_id=booking.id, amount=amount, currency="RUB"
            )
        )
        protection_task = asyncio.create_task(
            self._get_protection(booking, event, len(seats))
        )

        payment = await payment_task
        protection = await protection_task

        async with self.db.transaction() as db:
            booking = await db.booking_repository.get_for_update(booking.id)
            seats = await db.event_seats_repository.get_seats_for_update(booking_id=booking.id)

            booking.apply_pricing(
                amount=amount,
                payment_commission=payment.commission,
                protection_price=protection.price if protection else 0,
                with_protection=protection.available if protection else False,
            )

            if {seat.id for seat in seats} != reserved_ids:
                raise InvalidBookingStateError(
                    booking_id=booking.id, status=booking.status
                )

            await db.booking_repository.save_booking(booking)

        return Checkout(
            booking=booking,
            seats=seats,
            event=event,
            protection=protection,
            payment=payment,
        )

    async def _get_protection(
        self, booking: Booking, event: Event, ticket_amount: int
    ) -> Protection | None:
        try:
            async with asyncio.timeout(3):
                return await self.protection_connector.get_protection_availability(
                    booking_id=booking.id,
                    ticket_amount=ticket_amount,
                    event_category=event.category,
                    event_starts_at=event.starts_at,
                )
        except (TimeoutError, ProtectionServiceUnavailableError):
            return None
