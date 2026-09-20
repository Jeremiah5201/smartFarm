"""Send one controlled Africa's Talking sandbox SMS."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.config import load_settings
from app.intelligence.irrigation_engine import IrrigationThresholds
from app.intelligence.weather import WeatherData
from app.services.advisory import AdvisoryEvaluationInput
from app.services.advisory_notifications import evaluate_and_send_advisory


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/send_test_sms.py <approved-recipient-number>")
        return 2

    recipient = sys.argv[1].strip()
    settings = load_settings(BACKEND_ROOT / ".env")
    client = settings.create_sms_client()
    result = evaluate_and_send_advisory(
        farm=AdvisoryEvaluationInput(
            farm_id="FARM001",
            crop="maize",
            soil_moisture=25,
            soil_ph=6.4,
            temperature=27.8,
            humidity=71.2,
            rain_detected=False,
            water_level=78,
            location="Kampala",
            growth_stage="flowering",
        ),
        weather=WeatherData(
            rain_probability=15,
            temperature=27,
            humidity=70,
        ),
        thresholds=IrrigationThresholds(
            soil_moisture_threshold=30,
            forecast_rain_probability_threshold=40,
            minimum_water_level=20,
            duration_seconds=30,
        ),
        phone_number=recipient,
        sms_sender=client,
    )

    print(f"Advisory: {result.evaluation.advisory.message}")
    print(
        "Irrigation required: "
        f"{result.evaluation.irrigation.irrigation_required}"
    )
    print(f"SMS message:\n{result.message or 'No SMS sent'}")
    if result.delivery:
        print(f"SMS provider status: {result.delivery.status}")
        print(
            "Provider message ID: "
            f"{result.delivery.message_id or 'not supplied'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
