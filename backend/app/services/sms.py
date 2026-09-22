"""Farmer-facing SMS formatting and Africa's Talking delivery."""

from dataclasses import dataclass
import json
from typing import Any, Callable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.intelligence.crop_advisor import CropAdvisory
from app.intelligence.irrigation_engine import IrrigationInput

AFRICASTALKING_SMS_URL = "https://api.africastalking.com/version1/messaging"


@dataclass(frozen=True)
class SmsDeliveryResult:
    """Provider response needed for SMSLog persistence."""

    status: str
    message_id: Optional[str]
    response: Mapping[str, Any]


class AfricasTalkingSmsClient:
    """Minimal Africa's Talking SMS client with injectable HTTP transport."""

    def __init__(
        self,
        username: str,
        api_key: str,
        sender_id: Optional[str] = None,
        *,
        endpoint: str = AFRICASTALKING_SMS_URL,
        http_post: Optional[Callable[..., bytes]] = None,
    ) -> None:
        if not username.strip():
            raise ValueError("Africa's Talking username must not be empty")
        if not api_key.strip():
            raise ValueError("Africa's Talking API key must not be empty")
        self._username = username
        self._api_key = api_key
        self._sender_id = sender_id.strip() if sender_id else None
        self._endpoint = endpoint
        self._http_post = http_post or _post_form

    def send(self, phone_number: str, message: str) -> SmsDeliveryResult:
        """Send one SMS through Africa's Talking messaging endpoint."""

        phone_number = phone_number.strip()
        if not phone_number:
            raise ValueError("phone_number must not be empty")
        if not message.strip():
            raise ValueError("message must not be empty")

        form = {
            "username": self._username,
            "to": phone_number,
            "message": message,
        }
        if self._sender_id:
            form["from"] = self._sender_id

        raw_response = self._http_post(
            self._endpoint,
            form,
            {
                "apiKey": self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            15,
        )
        try:
            response = json.loads(raw_response.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError("Africa's Talking returned invalid JSON") from error
        if not isinstance(response, dict):
            raise RuntimeError("Africa's Talking returned an invalid response")

        recipient = _first_recipient(response)
        if recipient is None:
            provider_message = response.get("SMSMessageData", {}).get("Message")
            if isinstance(provider_message, str) and provider_message:
                raise RuntimeError(
                    f"Africa's Talking rejected the SMS: {provider_message}"
                )
            raise RuntimeError("Africa's Talking response contained no recipient")
        return SmsDeliveryResult(
            status=str(recipient.get("status", "unknown")),
            message_id=_optional_string(recipient.get("messageId")),
            response=response,
        )


def _first_recipient(response: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    entries = response.get("SMSMessageData", {}).get("Recipients", [])
    if not isinstance(entries, list) or not entries:
        return None
    recipient = entries[0]
    return recipient if isinstance(recipient, Mapping) else None


def _optional_string(value: Any) -> Optional[str]:
    return value if isinstance(value, str) and value else None


def _post_form(
    url: str,
    form: Mapping[str, str],
    headers: Mapping[str, str],
    timeout: int,
) -> bytes:
    request = Request(
        url,
        data=urlencode(form).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError("Africa's Talking SMS request failed") from error


def format_advisory_sms(
    crop: str,
    reading: IrrigationInput,
    soil_ph: float,
    advisory: CropAdvisory,
) -> str:
    """Format a short SMS without exposing backend or MQTT details."""

    crop = crop.strip()
    if not crop:
        raise ValueError("crop must not be empty")
    if not 0 <= reading.soil_moisture <= 100:
        raise ValueError("soil_moisture must be between 0 and 100")
    if reading.forecast_rain_probability is not None and not 0 <= reading.forecast_rain_probability <= 100:
        raise ValueError("forecast_rain_probability must be between 0 and 100")

    rain_probability = (
        "unknown"
        if reading.forecast_rain_probability is None
        else f"{reading.forecast_rain_probability:g}%"
    )
    return (
        f"SMARTFARM ALERT\n"
        f"{crop.title()} field\n"
        f"Soil moisture: {reading.soil_moisture:g}%\n"
        f"pH: {soil_ph:g}\n"
        f"Rain probability: {rain_probability}\n\n"
        f"Recommendation:\n{advisory.message}"
    )
