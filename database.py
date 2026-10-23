from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Property Rental Platform"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60

    # Default: local SQLite
    database_url: str = "sqlite:///./property_rental.db"

    upload_dir: str = "uploads"
    max_upload_size: int = 2 * 1024 * 1024
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

# Keep database-specific connection settings separate.
connect_args = {}

if settings.database_url.startswith("sqlite"):
    # Local SQLite configuration
    connect_args = {"check_same_thread": False}

elif settings.database_url.startswith("mysql+pymysql://"):
    # MySQL configuration
    if "aivencloud.com" in settings.database_url:
        # Aiven MySQL: verify the server using its CA certificate.
        ca_path = Path(__file__).resolve().parent / "certs" / "ca.pem"

        if not ca_path.is_file():
            raise FileNotFoundError(
                f"Aiven CA certificate not found: {ca_path}"
            )

        connect_args = {
            "ssl": {"ca": str(ca_path)}
        }

    else:
        # Local MySQL: use your local MySQL server configuration.
        connect_args = {}

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
