from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # === Environment ===
    environment: str = "development"

    # too weak: debug: bool = True
    @computed_field
    @property
    def debug(self) -> bool:
        return self.environment == "development"

    # === Database ===
    postgres_user: str = "user"
    postgres_password: str
    postgres_db: str = "db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        """Async database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync database URL for Alembic migrations."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # === CORS ===
    # In .env: ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
    # Leave empty in production and set explicitly via env var
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # === Auth ===
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. "
                'Generate one with: python -c "import secrets;'
                ' "print(secrets.token_hex(32))"'
            )
        return v

    secret_key: str
    jwt_algorithm: str = "HS256"
    # TODO: 7-day tokens, add revocation management
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days


settings = Settings()
