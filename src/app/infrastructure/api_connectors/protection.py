from datetime import datetime

import httpx

from app.application.exceptions import ProtectionServiceUnavailableError
from app.application.interfaces.connectors.protection_connector import (
    Protection,
    ProtectionConnector,
)
from app.infrastructure.api_connectors.base import BaseHTTPConnector


class HttpxProtectionConnector(BaseHTTPConnector, ProtectionConnector):
    async def get_protection_availability(
        self,
        booking_id: int,
        ticket_amount: int,
        event_category: str,
        event_starts_at: datetime,
    ) -> Protection:
        try:
            response = await self._request(
                "POST",
                "/protection/calculate",
                retry=True,
                json={
                    "booking_id": booking_id,
                    "ticket_amount": ticket_amount,
                    "event_category": event_category,
                    "event_starts_at": event_starts_at.isoformat(),
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProtectionServiceUnavailableError(
                f"HTTP {exc.response.status_code}"
            ) from exc
        except httpx.TransportError as exc:
            raise ProtectionServiceUnavailableError(type(exc).__name__) from exc

        data = response.json()
        return Protection(
            available=data["available"],
            price=data["price"],
            covered_amount=data["covered_amount"],
        )
