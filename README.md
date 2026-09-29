# API Афиши

Домашнее задание: блокировки в БД, конкурентные запросы к БД и внешним API, таймауты, retry, jitter и rate limiter.

## Запуск

```bash
docker compose up -d db payment-api protection-api   # Postgres :7432, Payment API :9001, Protection API :9002
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --app-dir src
```

Настройки читаются из `.env` в корне проекта (см. `.env-example`).

## Где искать то, что отрабатывается в ДЗ

| Тема | Место в коде |
|---|---|
| Блокировки в БД (`SELECT ... FOR UPDATE NOWAIT`) | `infrastructure/postgres/repositories/event_seats.py` -> `get_seats_for_reserve` |
| Конкурентные запросы к БД | `application/use_cases/get_event_dashboard.py` |
| Конкурентные запросы к внешним API | `application/use_cases/prepare_checkout.py` |
| Таймаут | `application/use_cases/prepare_checkout.py` -> `_get_protection`, `asyncio.timeout(3)` |
| Retry с экспоненциальным backoff и jitter | `infrastructure/api_connectors/base.py` |
| Rate limiter | `infrastructure/api_connectors/base.py` -> `RateLimiter` |

## Структура проекта

Для практики выбрана чистая архитектура.

```
src/app/
├── api/             роуты, pydantic-схемы, маппинг ошибок в HTTP-коды
├── application/     сценарии (use cases), интерфейсы репозиториев и коннекторов, DTO, ошибки сценариев
├── domain/          бизнес-сущности (Booking, EventSeat, Event), статусы, доменные ошибки
├── infrastructure/  реализации: Postgres-репозитории, httpx-коннекторы, модели SQLAlchemy
├── ioc.py           DI-контейнер на dishka: провайдеры для конфига, БД, коннекторов и use cases
└── main.py          сборка FastAPI-приложения
```

Используемые паттерны:
- **Unit of Work** `DatabaseManager.transaction()` (`infrastructure/postgres/db.py`) открывает транзакцию и отдаёт `UnitOfWork` с репозиториями на одной сессии
- **DI (dishka)** Use case получает зависимости через интерфейсы (`DatabaseManager`, `PaymentConnector`), реализации подставляет контейнер Dishka
