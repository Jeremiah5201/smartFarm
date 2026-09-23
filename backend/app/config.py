import os
from pathlib import Path
from typing import Mapping

from pydantic_settings import BaseSettings, SettingsConfigDict


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    database_url: str = "sqlite:///./smartfarm.db"
    mqtt_enabled: bool = True
    mqtt_host: str = "25982f992b5d422194eb3edfd0e2d2d1.s1.eu.hivemq.cloud"
    mqtt_port: int = 8883
    mqtt_username: str = "BackendSmartFarm"
    mqtt_password: str = "BackendSmartFarm"
    mqtt_tls: bool = True
    mqtt_telemetry_topic: str = "smartfarm/FARM001/telemetry"
    sms_provider: str = ""
    africastalking_username: str = ""
    africastalking_api_key: str = ""
    africastalking_base_url: str = "https://api.africastalking.com/version1/messaging"
    sms_sender_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def create_sms_client(self):
        if self.sms_provider.lower() != "africastalking":
            raise ValueError("SMS_PROVIDER must be africastalking")
        if not self.africastalking_api_key:
            raise ValueError("AFRICASTALKING_API_KEY is required")
        from app.services.sms import AfricasTalkingSmsClient

        return AfricasTalkingSmsClient(
            self.africastalking_username,
            self.africastalking_api_key,
            self.sms_sender_id or None,
            endpoint=self.africastalking_base_url,
        )


def load_settings(env_path: Path | None = None, environ: Mapping[str, str] | None = None) -> Settings:
    values = _read_env_file(env_path) if env_path else {}
    values.update(dict(environ if environ is not None else os.environ))
    settings = Settings.model_construct(**{
        key.lower(): value
        for key, value in values.items()
        if key in {
            "APP_ENV",
            "APP_PORT",
            "DATABASE_URL",
            "MQTT_ENABLED",
            "MQTT_HOST",
            "MQTT_PORT",
            "MQTT_USERNAME",
            "MQTT_PASSWORD",
            "MQTT_TLS",
            "MQTT_TELEMETRY_TOPIC",
            "SMS_PROVIDER",
            "AFRICASTALKING_USERNAME",
            "AFRICASTALKING_API_KEY",
            "AFRICASTALKING_BASE_URL",
            "SMS_SENDER_ID",
        }
    })
    if settings.sms_provider.lower() == "africastalking":
        if not settings.africastalking_username:
            raise ValueError("AFRICASTALKING_USERNAME is required")
        if not settings.africastalking_api_key:
            raise ValueError("AFRICASTALKING_API_KEY is required")
    return settings


settings = Settings()