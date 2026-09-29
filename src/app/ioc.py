from collections.abc import AsyncIterator

from app.application.interfaces.unit_of_work import DatabaseManager
from app.application.interfaces.connectors import ProtectionConnector, PaymentConnector
from app.application.use_cases import PrepareCheckoutUseCase, GetEventDashboardUseCase
from app.config import PostgresConfig, Settings, AppConfig, ConnectorsConfig
from app.infrastructure.postgres.db import SqlAlchemyDatabaseManager
from app.infrastructure.api_connectors import (
    HttpxPaymentConnector,
    HttpxProtectionConnector,
)

from dishka import Provider, Scope, make_async_container, provide, from_context, alias
from dishka.integrations.fastapi import FastapiProvider


class ConfigProvider(Provider):
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_postgres_config(self, settings: Settings) -> PostgresConfig:
        return settings.postgres

    @provide(scope=Scope.APP)
    def get_app_config(self, settings: Settings) -> AppConfig:
        return settings.app

    @provide(scope=Scope.APP)
    def get_connectors_config(self, settings: Settings) -> ConnectorsConfig:
        return settings.connectors


class PostgresProvider(Provider):
    @provide(scope=Scope.APP)
    async def database(
        self, config: PostgresConfig
    ) -> AsyncIterator[SqlAlchemyDatabaseManager]:
        db = SqlAlchemyDatabaseManager(config)
        yield db
        await db.close()

    db_interface = alias(SqlAlchemyDatabaseManager, provides=DatabaseManager)


class ConnectorProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_payment_connector(
        self,
        config: ConnectorsConfig,
    ) -> AsyncIterator[PaymentConnector]:
        payment_config = config.payment
        connector = HttpxPaymentConnector(
            base_url=payment_config.base_url,
            timeout=payment_config.timeout,
        )

        yield connector

        await connector.close_client()

    @provide(scope=Scope.APP)
    async def get_protection_connector(
        self,
        config: ConnectorsConfig,
    ) -> AsyncIterator[ProtectionConnector]:
        protection_config = config.protection
        connector = HttpxProtectionConnector(
            base_url=protection_config.base_url,
            timeout=protection_config.timeout,
        )

        yield connector

        await connector.close_client()


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_prepare_checkout_use_case(
        self,
        db: DatabaseManager,
        payment_connector: PaymentConnector,
        protection_connector: ProtectionConnector,
    ) -> PrepareCheckoutUseCase:
        return PrepareCheckoutUseCase(
            db=db,
            payment_connector=payment_connector,
            protection_connector=protection_connector,
        )

    @provide(scope=Scope.REQUEST)
    def get_event_dashboard_use_case(
        self,
        db: DatabaseManager,
    ) -> GetEventDashboardUseCase:
        return GetEventDashboardUseCase(db=db)


def create_container(settings: Settings):
    return make_async_container(
        ConfigProvider(),
        PostgresProvider(),
        ConnectorProvider(),
        UseCaseProvider(),
        FastapiProvider(),
        context={Settings: settings},
    )
