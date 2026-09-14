from sqlalchemy import insert, select, update, and_

from typing import Sequence
from datetime import datetime
from app.models import EventSeat, Booking, SeatStatus
from app.infrastructure.postgres.repositories.base import BaseRepo

class EventRepo(BaseRepo):
    async def get_seats_for_reserve(self, event_id: int, seat_ids: list[int]) -> Sequence[EventSeat]:
        query = select(EventSeat).where(
            and_(
                EventSeat.event_id == event_id,
                EventSeat.seat_id.in_(seat_ids)
            )
        ).with_for_update(nowait=True)

        return (await self.session.scalars(query)).all()
