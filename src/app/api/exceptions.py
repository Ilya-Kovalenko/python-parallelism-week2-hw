from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.exceptions import (
    ApplicationError,
    BookingNotFoundError,
    EventAccessDeniedError,
    EventNotFoundError,
    ExternalServiceUnavailableError,
    SeatNotFoundError,
    SeatReservationInProgressError,
)
from app.domain.exceptions import (
    BookingExpiredError,
    DomainError,
    InvalidBookingStateError,
    InvalidSeatStateError,
    SeatUnavailableError,
)

ERROR_RESPONSES: dict[type[Exception], tuple[int, str]] = {
    EventNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Мероприятие не найдено",
    ),
    BookingNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Бронь не найдена",
    ),
    SeatNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Некоторые места не найдены на мероприятии",
    ),
    EventAccessDeniedError: (
        status.HTTP_403_FORBIDDEN,
        "Вы не являетесь организатором этого мероприятия",
    ),
    ExternalServiceUnavailableError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Внешний сервис временно недоступен, попробуйте позже",
    ),
    SeatReservationInProgressError: (
        status.HTTP_409_CONFLICT,
        "Место в данный момент обрабатывается другим бронированием",
    ),
    SeatUnavailableError: (
        status.HTTP_409_CONFLICT,
        "Место недоступно для бронирования",
    ),
    BookingExpiredError: (
        status.HTTP_409_CONFLICT,
        "Срок брони истёк",
    ),
    InvalidBookingStateError: (
        status.HTTP_409_CONFLICT,
        "Бронь нельзя изменить в текущем статусе",
    ),
    InvalidSeatStateError: (
        status.HTTP_409_CONFLICT,
        "Место нельзя изменить в текущем статусе",
    ),
}


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    @app.exception_handler(DomainError)
    async def business_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        status_code, message = _get_error_response(exc)

        return JSONResponse(
            status_code=status_code,
            content={"detail": message},
        )


def _get_error_response(exc: Exception) -> tuple[int, str]:
    for error_type, response in ERROR_RESPONSES.items():
        if isinstance(exc, error_type):
            return response

    return status.HTTP_400_BAD_REQUEST, "Некорректный запрос"
