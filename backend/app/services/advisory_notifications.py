"""Advisory-to-SMS orchestration for SmartFarm."""

from dataclasses import dataclass
from typing import Protocol

from app.intelligence.irrigation_engine import IrrigationInput, IrrigationThresholds
from app.services.advisory import (
    AdvisoryEvaluation,
    AdvisoryEvaluationInput,
    evaluate_farm,
)
from app.services.sms import SmsDeliveryResult, format_advisory_sms
from app.intelligence.weather import WeatherData


class SmsSender(Protocol):
    """Small interface implemented by the Africa's Talking SMS client."""

    def send(self, phone_number: str, message: str) -> SmsDeliveryResult:
        ...


@dataclass(frozen=True)
class AdvisoryNotification:
    """Evaluation plus optional delivery result."""

    evaluation: AdvisoryEvaluation
    message: str | None
    delivery: SmsDeliveryResult | None


def evaluate_and_send_advisory(
    farm: AdvisoryEvaluationInput,
    weather: WeatherData,
    thresholds: IrrigationThresholds,
    phone_number: str,
    sms_sender: SmsSender,
) -> AdvisoryNotification:
    """Evaluate a farm and send an SMS for actionable advisories.

    INFO advisories are returned but not sent. This prevents routine
    notifications from consuming SMS balance; WARNING and CRITICAL advisories
    are treated as actionable.
    """

    evaluation = evaluate_farm(farm, weather, thresholds)
    if evaluation.advisory.severity == "INFO":
        return AdvisoryNotification(evaluation, None, None)

    sms_reading = IrrigationInput(
        soil_moisture=farm.soil_moisture,
        rain_detected=farm.rain_detected,
        forecast_rain_probability=weather.rain_probability,
        water_level=farm.water_level,
    )
    message = format_advisory_sms(
        farm.crop,
        sms_reading,
        farm.soil_ph,
        evaluation.advisory,
    )
    delivery = sms_sender.send(phone_number, message)
    return AdvisoryNotification(evaluation, message, delivery)
