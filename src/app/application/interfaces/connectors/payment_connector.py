from abc import ABC, abstractmethod
from app.application.dto import Payment


class PaymentConnector(ABC):
    @abstractmethod
    async def get_payment(
        self,
        booking_id: int,
        amount: int,
        currency: str,
    ) -> Payment: ...
