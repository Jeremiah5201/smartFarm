"""Environment-backed configuration for SmartFarm services."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping, Optional

from app.services.sms import AfricasTalkingSmsClient


@dataclass(frozen=True)
class Settings:
    """Runtime settings required by Member 3 services."""

    app_env: str
    weather_provider: str
    weather_base_url: str
    sms_provider: str
    africastalking_username: str
    africastalking_api_key: str
    africastalking_base_url: str
    sms_sender_id: Optional[str]

    def create_sms_client(self) -> AfricasTalkingSmsClient:
        """Create the configured Africa's Talking client."""

        if self.sms_provider.lower() != "africastalking":
            raise ValueError(
                f"unsupported SMS_PROVIDER: {self.sms_provider!r}; "
                "only 'africastalking' is supported"
            )
        return AfricasTalkingSmsClient(
            username=self.africastalking_username,
            api_key=self.africastalking_api_key,
            sender_id=self.sms_sender_id,
            endpoint=self.africastalking_base_url,
        )


def load_settings(
    env_path: Optional[Path] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> Settings:
    """Load settings from an optional local .env and process environment.

    Process environment values take precedence over values in the local file.
    The local .env is intentionally not loaded into global process state.
    """

    values = {}
    if env_path is not None:
        values.update(_read_env_file(env_path))
    source = os.environ if environ is None else environ
    values.update(source)

    return Settings(
        app_env=values.get("APP_ENV", "development"),
        weather_provider=values.get("WEATHER_PROVIDER", "open-meteo"),
        weather_base_url=values.get(
            "WEATHER_BASE_URL", "https://api.open-meteo.com/v1/forecast"
        ),
        sms_provider=_required(values, "SMS_PROVIDER"),
        africastalking_username=_required(values, "AFRICASTALKING_USERNAME"),
        africastalking_api_key=_required(values, "AFRICASTALKING_API_KEY"),
        africastalking_base_url=values.get(
            "AFRICASTALKING_BASE_URL",
            "https://api.sandbox.africastalking.com/version1/messaging",
        ),
        sms_sender_id=values.get("SMS_SENDER_ID") or None,
    )


def _required(values: Mapping[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise ValueError(f"missing required configuration: {name}")
    return value


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(f"environment file not found: {path}")

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"invalid environment entry on line {line_number}")
        name, value = line.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError(f"empty environment name on line {line_number}")
        values[name] = value.strip().strip('"').strip("'")
    return values
