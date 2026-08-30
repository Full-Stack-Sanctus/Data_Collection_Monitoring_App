from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    app_name: str = (
        "Digital Data Collection & Program Monitoring System"
    )

    app_env: str = "development"

    debug: bool = False

    database_url: str

    api_prefix: str = "/api"

    cors_origins: list[str] = Field(
        default_factory=list,
    )

    max_page_size: int = Field(
        default=100,
        gt=0,
    )

    default_page_size: int = Field(
        default=20,
        gt=0,
    )
    
    # This instructs Pydantic to search your environment block for these keys on boot.
    api_auth_enabled: bool
    api_key: str | None = None  # Optional type, but can be forced via validation if enabled
    

    # Authentication

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    jwt_access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
    )

    # KoboToolbox

    kobo_base_url: str = (
        "https://kf.kobotoolbox.org"
    )

    kobo_api_token: str

    kobo_asset_uid: str

    kobo_request_timeout_seconds: int = Field(
        default=30,
        gt=0,
    )

    data_directory: Path = (
        PROJECT_ROOT / "data"
    )

    raw_data_directory: Path = (
        PROJECT_ROOT / "data" / "raw"
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
        
    
settings = Settings()