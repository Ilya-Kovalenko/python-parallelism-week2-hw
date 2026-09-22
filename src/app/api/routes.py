from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.api.schemas import (
    BookingCreate,
    CheckoutBooking,
    CheckoutResponse,
    EventCreate,
    EventDashboard,
    EventRead,
    OccupancyDashboard,
    SalesDashboard,
    EventSeatRead,
    LocationDetail,
    LocationRead,
    PaymentCompleted,
    PaymentCreate,
    PaymentQuote,
    ProtectionQuote,
    SeatRead,
)
from app.application.use_cases import PrepareCheckoutUseCase, GetEventDashboardUseCase
from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)

router = APIRouter(route_class=DishkaRoute)


def get_current_user_id(x_user_id: Annotated[int, Header()]) -> int:
    return x_user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


@router.get("/locations")
async def list_locations() -> list[LocationRead]:
    """Возвращает список площадок."""
    ...


@router.get("/locations/{location_id}")
async def get_location(location_id: int) -> LocationDetail:
    """Возвращает площадку со схемой мест."""
    ...


@router.get("/locations/{location_id}/seats")
async def list_location_seats(location_id: int) -> list[SeatRead]:
    """Возвращает все места площадки."""
    ...


@router.get("/events")
async def list_events() -> list[EventRead]:
    """Возвращает список мероприятий для клиента."""
    ...


@router.get("/events/{event_id}")
async def get_event(event_id: int) -> EventRead:
    """Возвращает описание мероприятия."""
    ...


@router.get("/events/{event_id}/seats")
async def list_event_seats(event_id: int) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    ...


@router.get("/organizer/events")
async def list_organizer_events(organizer_id: CurrentUserId) -> list[EventRead]:
    """Возвращает список созданных событий текущего организатора."""
    ...


@router.post("/organizer/events")
async def create_event(payload: EventCreate, organizer_id: CurrentUserId) -> EventRead:
    """Создает мероприятие от лица текущего организатора."""
    ...


@router.get("/organizer/events/{event_id}/dashboard")
async def get_event_dashboard(
        event_id: int,
        organizer_id: CurrentUserId,
        use_case: FromDishka[GetEventDashboardUseCase],
) -> EventDashboard:
    """Возвращает аналитические данные для дашборда по мероприятию."""
    dashboard = await use_case.execute(event_id=event_id, organizer_id=organizer_id)

    sales = dashboard.sales
    occupancy = dashboard.occupancy

    return EventDashboard(
        event_title=dashboard.event.title,
        starts_at=dashboard.event.starts_at,
        sales=SalesDashboard(
            paid_orders=sales.paid_orders,
            sold_tickets=occupancy.sold,
            revenue=sales.revenue,
            average_order=sales.average_order,
        ),
        occupancy=OccupancyDashboard(
            total=occupancy.total,
            available=occupancy.available,
            reserved=occupancy.reserved,
            sold=occupancy.sold,
            occupancy_percent=occupancy.occupancy_percent,
        ),
    )

@router.post("/events/{event_id}/checkout")
async def prepare_checkout(
    event_id: int,
    payload: BookingCreate,
    user_id: CurrentUserId,
    use_case: FromDishka[PrepareCheckoutUseCase],
) -> CheckoutResponse:
    """Временно бронирует места за клиентом, возвращает итоговую стоимость
        и возможность страховки."""

    checkout = await use_case.execute(event_id=event_id, seat_ids=payload.seat_ids, user_id=user_id)

    booking = checkout.booking
    event = checkout.event
    protection = checkout.protection
    payment = checkout.payment

    return CheckoutResponse(
        booking=CheckoutBooking(
            id=booking.id,
            event_title=event.title,
            starts_at=event.starts_at,
            seats=[
                {"id": seat.id, "seat_id": seat.seat_id, "price": seat.price}
                for seat in checkout.seats
            ],
            base_amount=booking.amount,
            payment_commission=booking.payment_commission,
            protection_price=booking.protection_price,
            with_protection=booking.with_protection,
            reserved_until=booking.reserved_until,
        ),
        payment=PaymentQuote(
            commission=payment.commission,
            total=payment.total,
            payment_methods=payment.payment_methods,
            expires_at=payment.expires_at,
        ),
        protection=(
            ProtectionQuote(
                available=protection.available,
                price=protection.price,
                covered_amount=protection.covered_amount,
            )
            if protection else None
        ),
    )


@router.post("/bookings/{booking_id}/pay")
async def pay_booking(
    booking_id: int,
    payload: PaymentCreate,
    user_id: CurrentUserId,
) -> PaymentCompleted:
    """Принимает способ оплаты и флаг with_protection."""
    ...
