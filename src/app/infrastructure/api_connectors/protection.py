from datetime import datetime

from app.infrastructure.api_connectors.base import BaseHTTPConnector
from app.application.interfaces.connectors.protection_connector import (
    Protection,
    ProtectionConnector,
)


class HttpxProtectionConnector(BaseHTTPConnector, ProtectionConnector):
    async def get_protection_availability(
        self,
        booking_id: int,
        ticket_amount: int,
        event_category: str,
        event_starts_at: datetime,
    ) -> Protection:
        response = await self._request(
            "POST",
            "/protection/calculate",
            json={
                "booking_id": booking_id,
                "ticket_amount": ticket_amount,
                "event_category": event_category,
                "event_starts_at": event_starts_at.isoformat(),
            },
        )
        response.raise_for_status()

        data = response.json()
        return Protection(
            available=data["available"],
            price=data["price"],
            covered_amount=data["covered_amount"],
        )
