from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    database_url: str = "sqlite:///./smartfarm.db"
    mqtt_enabled: bool = False
    mqtt_host: str = ""
    mqtt_port: int = 8883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_tls: bool = True
    mqtt_telemetry_topic: str = "smartfarm/+/telemetry"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()