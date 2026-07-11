from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Sonya Lab API"
    app_env: str = "local"
    frontend_origin: str = "http://localhost:5173"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sonya_lab"
    openai_api_key: str = ""
    sonya_os_webhook_url: str = ""
    sonya_life_webhook_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
