from app.infrastructure.api_connectors.base import BaseHTTPConnector
from app.application.interfaces.connectors.payment_connector import (
    PaymentConnector,
    Payment,
)
from datetime import datetime


class HttpxPaymentConnector(BaseHTTPConnector, PaymentConnector):
    async def get_payment(
        self,
        booking_id: int,
        amount: int,
        currency: str,
    ) -> Payment:
        response = await self._request(
            "POST",
            "/payment/calculate",
            json={
                "booking_id": booking_id,
                "amount": amount,
                "currency": currency,
            },
        )
        response.raise_for_status()

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
