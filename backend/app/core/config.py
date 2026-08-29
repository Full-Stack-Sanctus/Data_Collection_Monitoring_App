from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Sensitive values such as database credentials and Kobo API tokens
    are loaded from the .env file and must never be committed to Git.
    """

    app_name: str = (
        "Digital Data Collection & Program Monitoring System"
    )

    app_env: str = "development"

    debug: bool = True

    database_url: str

    # API authentication

    api_key: str = Field(
        default="",
        min_length=0,
    )

    api_auth_enabled: bool = True

    # KoboToolbox API configuration

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