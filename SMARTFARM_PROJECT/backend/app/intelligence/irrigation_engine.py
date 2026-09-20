## Pure irrigation decision logic for SmartFarm.

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class IrrigationThresholds:
    """Configurable limits used by the initial irrigation rule."""

    soil_moisture_threshold: float
    forecast_rain_probability_threshold: float
    minimum_water_level: float
    duration_seconds: int = 30

    def __post_init__(self) -> None:
        if not 0 <= self.soil_moisture_threshold <= 100:
            raise ValueError("soil_moisture_threshold must be between 0 and 100")
        if not 0 <= self.forecast_rain_probability_threshold <= 100:
            raise ValueError(
                "forecast_rain_probability_threshold must be between 0 and 100"
            )
        if not 0 <= self.minimum_water_level <= 100:
            raise ValueError("minimum_water_level must be between 0 and 100")
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be greater than zero")


@dataclass(frozen=True)
class IrrigationInput:
    """Sensor and weather values required by the irrigation rule."""

    soil_moisture: float
    rain_detected: bool
    forecast_rain_probability: Optional[float]
    water_level: float


@dataclass(frozen=True)
class IrrigationDecision:
    """Explainable result of an irrigation evaluation."""

    irrigation_required: bool
    pump: bool
    duration_seconds: int
    reason: str


def decide_irrigation(
    reading: IrrigationInput,
    thresholds: IrrigationThresholds,
) -> IrrigationDecision:
    """Evaluate the specification's initial irrigation rule.

    Missing forecast data prevents automatic irrigation because the rule
    requires a forecast probability to be below its configured threshold.
    """

    if reading.soil_moisture >= thresholds.soil_moisture_threshold:
        return _no_irrigation("Soil moisture is at or above the configured threshold.")

    if reading.rain_detected:
        return _no_irrigation("Rain has been detected.")

    if reading.forecast_rain_probability is None:
        return _no_irrigation("Rain forecast data is unavailable.")

    if not 0 <= reading.forecast_rain_probability <= 100:
        raise ValueError("forecast_rain_probability must be between 0 and 100")

    if (
        reading.forecast_rain_probability
        >= thresholds.forecast_rain_probability_threshold
    ):
        return _no_irrigation(
            "Forecast rain probability is at or above the configured threshold."
        )

    if reading.water_level <= thresholds.minimum_water_level:
        return _no_irrigation(
            "Water level is at or below the configured minimum."
        )

    return IrrigationDecision(
        irrigation_required=True,
        pump=True,
        duration_seconds=thresholds.duration_seconds,
        reason=(
            "Soil moisture is below the configured threshold, rain probability "
            "is low, and sufficient water is available."
        ),
    )


def _no_irrigation(reason: str) -> IrrigationDecision:
    return IrrigationDecision(
        irrigation_required=False,
        pump=False,
        duration_seconds=0,
        reason=reason,
    )
