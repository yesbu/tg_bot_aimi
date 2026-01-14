from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="postgres", description="PostgreSQL password")
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5433, ge=1024, le=65535)
    POSTGRES_DB: str = Field(default="aimi_subscription", description="Database name")

    @computed_field
    @property
    def URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1024, le=65535)
    REDIS_DB: int = Field(default=0, ge=0, le=15)
    REDIS_PASSWORD: str | None = Field(default=None, description="Redis password (optional)")

    @computed_field
    @property
    def URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def host(self) -> str:
        return self.REDIS_HOST
    
    @property
    def port(self) -> int:
        return self.REDIS_PORT
    
    @property
    def db(self) -> int:
        return self.REDIS_DB
    
    @property
    def password(self) -> str | None:
        return self.REDIS_PASSWORD



class PaymentSettings(BaseSettings):
    PAYMENT_BASE_URL: str = Field(
        default="https://sps.airbapay.kz/acquiring-api",
        description="Payment gateway base URL"
    )

    PAYMENT_USER: str = Field(default="Test-AMANATGENERATION")
    PAYMENT_PASSWORD: str = Field(default="awz4f~pz-v3!qpNd")
    PAYMENT_TERMINAL_ID: str = Field(default="67b32a6bc908cc488ae9c3ed")


class TelegramSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = Field(description="Telegram Bot API token", default="8478053802:AAGnM34vp6mAyDNyuXfxkj3kqxcoQoRRArc")

    @field_validator("TELEGRAM_BOT_TOKEN")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v or len(v) < 45 or ":" not in v:
            raise ValueError("Invalid Telegram bot token format")
        return v

class Settings(BaseSettings):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    payment: PaymentSettings = Field(default_factory=PaymentSettings)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()

