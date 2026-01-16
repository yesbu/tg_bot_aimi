from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str = Field(..., description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    POSTGRES_HOST: str = Field(..., description="PostgreSQL host")
    POSTGRES_PORT: int = Field(..., ge=1024, le=65535)
    POSTGRES_DB: str = Field(..., description="Database name")

    @computed_field
    @property
    def URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(..., description="Redis host")
    REDIS_PORT: int = Field(..., ge=1024, le=65535)
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

    PAYMENT_USER: str = Field(..., description="Payment gateway username")
    PAYMENT_PASSWORD: str = Field(..., description="Payment gateway password")
    PAYMENT_TERMINAL_ID: str = Field(..., description="Payment gateway terminal ID")


class TelegramSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API token")

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

