from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Sonya Lab API"
    service_name: str = "sonya-lab-backend"
    app_env: str = "local"
    frontend_origin: str = "http://localhost:5175"
    backend_port: int = 8002
    database_url: str = "postgresql+psycopg://sonya_lab_app:sonya_lab_dev@localhost:55432/sonya_lab"
    single_user_mode: bool = True
    single_user_id: str = "local-user"
    timezone: str = "Asia/Seoul"
    default_currency: str = "KRW"
    flight_provider: str = "mock"
    flight_booking_allowed_domains: str = ""
    paper_provider: str = "crossref"
    minimum_collection_interval_minutes: int = 60
    scheduler_poll_seconds: int = 30
    openai_api_key: str = ""
    crossref_mailto: str = ""
    paper_api_timeout_seconds: float = 15.0
    paper_summary_model: str = "gpt-5.4-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
