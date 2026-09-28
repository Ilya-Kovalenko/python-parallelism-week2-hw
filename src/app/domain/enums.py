import enum


class SeatStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class BookingStatus(str, enum.Enum):
    PREPARING = "preparing"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
