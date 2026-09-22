from sqlalchemy import select, update, and_, func
from sqlalchemy.exc import OperationalError


from typing import Sequence
from app.domain.enums import SeatStatus
from app.application.dto import OccupancyStats
from app.domain.entities import EventSeat as EventSeatEntity
from app.application.interfaces.repositories import EventSeatsRepository
from app.application.exceptions import SeatNotFoundError, SeatReservationInProgressError
from app.infrastructure.postgres.models import EventSeat
from app.infrastructure.postgres.repositories.base import BaseRepository


class PostgresEventSeatsRepository(BaseRepository, EventSeatsRepository):
    async def get_seats_for_reserve(self, event_id: int, seat_ids: Sequence[int]) -> Sequence[EventSeat]:
        query = select(EventSeat).where(
            and_(
                EventSeat.event_id == event_id,
                EventSeat.seat_id.in_(seat_ids)
            )
        ).with_for_update(nowait=True)

        try:
            event_seats = (await self.session.scalars(query)).all()
        except OperationalError as exc:
            sqlstate = getattr(exc.orig, "sqlstate", None)
            if sqlstate == "55P03":
                raise SeatReservationInProgressError from exc
            raise

        missing = set(seat_ids) - {seat.seat_id for seat in event_seats}
        if missing:
            raise SeatNotFoundError(event_id=event_id, seat_ids=sorted(missing))

        return [self._to_domain(seat) for seat in event_seats]

    async def save_many(self, seats: Sequence[EventSeatEntity]) -> None:
        for seat in seats:
            result = await self.session.execute(
                update(EventSeat)
                .where(EventSeat.id == seat.id)
                .values(
                    status=seat.status,
                    booking_id=seat.booking_id,
                    reserved_until=seat.reserved_until
                )
            )

            if result.rowcount != 1:
                raise SeatNotFoundError(event_id=seat.event_id, seat_ids=[seat.seat_id])

    async def get_occupancy_stats(self, event_id: int) -> OccupancyStats:
        query = (
            select(EventSeat.status, func.count(EventSeat.id))
            .where(EventSeat.event_id == event_id)
            .group_by(EventSeat.status)
        )

        counts = dict((await self.session.execute(query)).all())

        available = counts.get(SeatStatus.AVAILABLE, 0)
        reserved = counts.get(SeatStatus.RESERVED, 0)
        sold = counts.get(SeatStatus.SOLD, 0)
        total = available + reserved + sold

        return OccupancyStats(
            total=total,
            available=available,
            reserved=reserved,
            sold=sold,
            occupancy_percent=round((reserved + sold) / total * 100, 2) if total else 0.0,
        )

    @staticmethod
    def _to_domain(event_seat: EventSeat) -> EventSeatEntity:
        return EventSeatEntity(
            id=event_seat.id,
            event_id=event_seat.event_id,
            seat_id=event_seat.seat_id,
            price=event_seat.price,
            status=event_seat.status,
            reserved_until=event_seat.reserved_until,
            booking_id=event_seat.booking_id
        )
