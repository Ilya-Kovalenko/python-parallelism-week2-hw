from sqlalchemy import select
from app.application.exceptions import EventNotFoundError
from app.application.interfaces.repositories import EventRepository
from app.domain.entities import Event as EventEntity
from app.infrastructure.postgres.models import Event
from app.infrastructure.postgres.repositories.base import BaseRepository


class PostgresEventRepository(BaseRepository, EventRepository):
    async def get_event(self, event_id: int) -> EventEntity:
        query = select(Event).where(Event.id == event_id)

        event = (await self.session.scalars(query)).one_or_none()
        if event is None:
            raise EventNotFoundError(event_id)

        return EventEntity(
            id=event.id,
            organizer_id=event.organizer_id,
            location_id=event.location_id,
            title=event.title,
            description=event.description,
            category=event.category,
            starts_at=event.starts_at,
            base_price=event.base_price
        )
