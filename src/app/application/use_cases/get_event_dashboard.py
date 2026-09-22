import asyncio

from app.application.exceptions import EventAccessDeniedError
from app.application.interfaces.unit_of_work import DatabaseManager
from app.application.dto import OccupancyStats, SalesStats, EventDashboard


class GetEventDashboardUseCase:
    def __init__(
        self,
        db: DatabaseManager,
    ) -> None:
        self.db = db

    async def execute(self, event_id: int, organizer_id: int) -> EventDashboard:
        async with self.db.transaction() as db:
            event = await db.event_repository.get_event(event_id=event_id)

            if event.organizer_id != organizer_id:
                raise EventAccessDeniedError(event_id=event_id, organizer_id=organizer_id)

        async with asyncio.TaskGroup() as tg:
            sales_task = tg.create_task(self._load_sales(event_id))
            occupancy_task = tg.create_task(self._load_occupancy(event_id))

        return EventDashboard(
            event=event,
            sales=sales_task.result(),
            occupancy=occupancy_task.result()
        )

    async def _load_sales(self, event_id: int) -> SalesStats:
        async with self.db.transaction() as db:
            return await db.booking_repository.get_sales_stats(event_id)

    async def _load_occupancy(self, event_id: int) -> OccupancyStats:
        async with self.db.transaction() as db:
            return await db.event_seats_repository.get_occupancy_stats(event_id)
