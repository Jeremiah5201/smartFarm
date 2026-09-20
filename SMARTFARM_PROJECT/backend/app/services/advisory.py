"""Application service for producing SmartFarm advisories."""

from dataclasses import dataclass

from app.intelligence.crop_advisor import (
    CropAdvisory,
    CropAdvisoryInput,
    generate_crop_advisory,
)
from app.intelligence.irrigation_engine import (
    IrrigationDecision,
    IrrigationInput,
    IrrigationThresholds,
    decide_irrigation,
)
from app.intelligence.weather import WeatherData


@dataclass(frozen=True)
class AdvisoryEvaluationInput:
    """Farm and latest-reading values needed for one evaluation."""

    farm_id: str
    crop: str
    soil_moisture: float
    soil_ph: float
    temperature: float
    humidity: float
    rain_detected: bool
    water_level: float
    location: str = ""
    growth_stage: str = "unknown"


@dataclass(frozen=True)
class AdvisoryEvaluation:
    """Combined irrigation and crop-advisory result."""

    farm_id: str
    irrigation: IrrigationDecision
    advisory: CropAdvisory
    weather: WeatherData


def evaluate_farm(
    farm: AdvisoryEvaluationInput,
    weather: WeatherData,
    thresholds: IrrigationThresholds,
) -> AdvisoryEvaluation:
    """Evaluate one farm using normalized weather data and configured rules."""

    if not farm.farm_id.strip():
        raise ValueError("farm_id must not be empty")

    irrigation = decide_irrigation(
        IrrigationInput(
            soil_moisture=farm.soil_moisture,
            rain_detected=farm.rain_detected,
            forecast_rain_probability=weather.rain_probability,
            water_level=farm.water_level,
        ),
        thresholds,
    )
    advisory = generate_crop_advisory(
        CropAdvisoryInput(
            crop=farm.crop,
            soil_ph=farm.soil_ph,
            soil_moisture=farm.soil_moisture,
            temperature=farm.temperature,
            humidity=farm.humidity,
            location=farm.location,
            growth_stage=farm.growth_stage,
        ),
        irrigation,
    )
    return AdvisoryEvaluation(
        farm_id=farm.farm_id,
        irrigation=irrigation,
        advisory=advisory,
        weather=weather,
    )
