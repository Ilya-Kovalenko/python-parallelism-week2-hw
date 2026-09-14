# TODO: может быть это не events домен. И Ещё подумать может рефактор на use cases, а не Services

from app.infrastructure.db import DatabaseManager
from datetime import datetime, UTC, timedelta

class EventsService:
    def __init__(
        self,
        db: DatabaseManager
    ) -> None:
        self.db = db

    async def prepare_checkout(self, event_id: int, seat_ids: list[int], user_id: int):
        reversed_until = datetime.now(UTC) + timedelta(minutes=15)

        async with self.db.transaction() as db:
            seats = await db.event_repo.get_seats_for_reserve(event_id=event_id, seat_ids=seat_ids)




        # 1. TODO: select for update на места на 15 минут

        # 2. TODO: конкурентно запросить Payment API и Protection API для расчета checkout.

        # TODO: а как через 15 минут сбросить бронь и booking?)
