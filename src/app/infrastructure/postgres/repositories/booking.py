from sqlalchemy import select, update, func

from datetime import datetime

from app.application.exceptions import BookingNotFoundError
from app.application.interfaces.repositories import BookingRepository
from app.infrastructure.postgres.models import Booking, BookingStatus
from app.domain.entities import Booking as BookingEntity
from app.infrastructure.postgres.repositories.base import BaseRepository
from app.application.dto import SalesStats


class PostgresBookingRepository(BaseRepository, BookingRepository):
    async def create_booking(self, event_id: int, user_id: int, reserved_until: datetime) -> BookingEntity:
        booking = Booking(
            event_id=event_id,
            user_id=user_id,
            amount=0,
            payment_commission=0,
            protection_price=None,
            with_protection=False,
            reserved_until=reserved_until
        )

        self.session.add(booking)
        await self.session.flush()

        return self._to_domain(booking)

    async def save_booking(self, booking: BookingEntity) -> None:
        result = await self.session.execute(
            update(Booking)
            .where(Booking.id == booking.id)
            .values(
                amount=booking.amount,
                payment_commission=booking.payment_commission,
                protection_price=booking.protection_price,
                with_protection=booking.with_protection,
                status=booking.status,
            )
        )

        if result.rowcount != 1:
            raise BookingNotFoundError(booking.id)

    async def get_sales_stats(self, event_id: int) -> SalesStats:
        query = select(
            func.count(Booking.id),
            func.coalesce(func.sum(Booking.amount), 0),
        ).where(
            Booking.event_id == event_id,
            Booking.status == BookingStatus.PAID,
        )

        paid_orders, revenue = (await self.session.execute(query)).one()

        return SalesStats(
            paid_orders=paid_orders,
            revenue=revenue,
            average_order=revenue // paid_orders if paid_orders else 0,
        )

    @staticmethod
    def _to_domain(booking: Booking) -> BookingEntity:
        return BookingEntity(
            id = booking.id,
            event_id = booking.event_id,
            user_id = booking.user_id,
            amount = booking.amount,
            payment_commission = booking.payment_commission,
            protection_price = booking.protection_price,
            with_protection = booking.with_protection,
            status = booking.status,
            reserved_until = booking.reserved_until
        )
