"""Weather data normalization and Open-Meteo integration for SmartFarm."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any, Callable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass(frozen=True)
class WeatherData:
    """Provider-independent weather values used by intelligence rules."""

    rain_probability: Optional[float]
    temperature: Optional[float]
    humidity: Optional[float]

    def __post_init__(self) -> None:
        if self.rain_probability is not None and not 0 <= self.rain_probability <= 100:
            raise ValueError("rain_probability must be between 0 and 100")
        if self.humidity is not None and not 0 <= self.humidity <= 100:
            raise ValueError("humidity must be between 0 and 100")


def normalize_weather_response(response: Mapping[str, Any]) -> WeatherData:
    """Convert a normalized or provider-adapter response into WeatherData.

    The first implementation accepts the small internal shape agreed for
    testing. Provider-specific HTTP clients should map their responses to this
    shape before calling this function.
    """

    if not isinstance(response, Mapping):
        raise TypeError("weather response must be a mapping")

    return WeatherData(
        rain_probability=_optional_number(response, "rain_probability"),
        temperature=_optional_number(response, "temperature"),
        humidity=_optional_number(response, "humidity"),
    )


def fetch_open_meteo_weather(
    latitude: float,
    longitude: float,
    *,
    http_get: Optional[Callable[[str, int], Mapping[str, Any]]] = None,
    base_url: str = "https://api.open-meteo.com/v1/forecast",
) -> WeatherData:
    """Fetch the current hourly forecast needed by the irrigation rule.

    ``http_get`` is injectable so unit tests do not need network access. The
    ESP32's ``rain_detected`` value remains separate and is supplied by
    ``AdvisoryEvaluationInput``.
    """

    _validate_coordinate(latitude, "latitude", -90, 90)
    _validate_coordinate(longitude, "longitude", -180, 180)
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": (
                "temperature_2m,relative_humidity_2m,"
                "precipitation_probability"
            ),
            "forecast_days": 2,
            "timezone": "UTC",
        }
    )
    request_url = f"{base_url}?{query}"
    getter = http_get or _http_get_json
    response = getter(request_url, 10)
    return _normalize_open_meteo_response(response)


def _normalize_open_meteo_response(response: Mapping[str, Any]) -> WeatherData:
    hourly = response.get("hourly")
    if not isinstance(hourly, Mapping):
        raise ValueError("Open-Meteo response is missing hourly data")

    times = hourly.get("time")
    probabilities = hourly.get("precipitation_probability")
    temperatures = hourly.get("temperature_2m")
    humidities = hourly.get("relative_humidity_2m")
    if not all(isinstance(values, list) for values in (
        times,
        probabilities,
        temperatures,
        humidities,
    )):
        raise ValueError("Open-Meteo hourly fields must be arrays")
    if not times:
        raise ValueError("Open-Meteo returned no hourly forecast values")

    index = _first_current_or_future_index(times)
    return normalize_weather_response(
        {
            "rain_probability": probabilities[index],
            "temperature": temperatures[index],
            "humidity": humidities[index],
        }
    )


def _first_current_or_future_index(times: list[Any]) -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for index, value in enumerate(times):
        if not isinstance(value, str):
            raise ValueError("Open-Meteo forecast times must be strings")
        try:
            forecast_time = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError("Open-Meteo returned an invalid forecast time") from error
        if forecast_time >= now:
            return index
    return len(times) - 1


def _http_get_json(url: str, timeout: int) -> Mapping[str, Any]:
    try:
        with urlopen(url, timeout=timeout) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("Open-Meteo request failed") from error


def _validate_coordinate(
    value: float,
    field: str,
    minimum: float,
    maximum: float,
) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    if not minimum <= value <= maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")


def _optional_number(response: Mapping[str, Any], field: str) -> Optional[float]:
    value = response.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number or null")
    return float(value)
