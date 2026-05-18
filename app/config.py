from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    teams_webhook_url: str
    app_env: str = "local"
    database_path: str = "./data/bridge_messages.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()