from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    host: str
    port: int
    reload: bool
    payment_api_url: str
    protection_api_url: str
    booking_ttl_minutes: int


class PostgresConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str

    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:"
            f"{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class RedisConfig(BaseModel):
    host: str
    port: int
    password: SecretStr | None = None
    database: int = 0

    @property
    def url(self) -> str:
        if self.password is None:
            return f"redis://{self.host}:{self.port}/{self.database}"

        password = self.password.get_secret_value()
        return f"redis://:{password}@{self.host}:{self.port}/{self.database}"


class PaymentApiConfig(BaseModel):
    base_url: str
    timeout: float = 5.0


class ProtectionApiConfig(BaseModel):
    base_url: str
    timeout: float = 5.0


class ConnectorsConfig(BaseModel):
    payment: PaymentApiConfig
    protection: ProtectionApiConfig


class Settings(BaseSettings):
    app: AppConfig
    postgres: PostgresConfig
    redis: RedisConfig
    connectors: ConnectorsConfig

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
