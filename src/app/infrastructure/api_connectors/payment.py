from datetime import datetime

import httpx

from app.application.exceptions import PaymentServiceUnavailableError
from app.application.interfaces.connectors.payment_connector import (
    Payment,
    PaymentConnector,
)
from app.infrastructure.api_connectors.base import BaseHTTPConnector


class HttpxPaymentConnector(BaseHTTPConnector, PaymentConnector):
    async def get_payment(
        self,
        booking_id: int,
        amount: int,
        currency: str,
    ) -> Payment:
        try:
            response = await self._request(
                "POST",
                "/payment/calculate",
                retry=True,
                json={
                    "booking_id": booking_id,
                    "amount": amount,
                    "currency": currency,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PaymentServiceUnavailableError(
                f"HTTP {exc.response.status_code}"
            ) from exc
        except httpx.TransportError as exc:
            raise PaymentServiceUnavailableError(type(exc).__name__) from exc

        data = response.json()
        expires_at_raw = data.get("expires_at")

        return Payment(
            commission=int(data["commission"]),
            total=int(data["total"]),
            payment_methods=list(data["payment_methods"]),
            expires_at=datetime.fromisoformat(expires_at_raw)
            if expires_at_raw
            else None,
        )
