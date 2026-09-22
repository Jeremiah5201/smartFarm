import unittest

from app.intelligence.irrigation_engine import IrrigationThresholds
from app.intelligence.weather import WeatherData
from app.services.advisory import AdvisoryEvaluationInput
from app.services.advisory_notifications import evaluate_and_send_advisory
from app.services.sms import SmsDeliveryResult


class FakeSmsSender:
    def __init__(self):
        self.sent = []

    def send(self, phone_number, message):
        self.sent.append((phone_number, message))
        return SmsDeliveryResult("Success", "ATX-test", {"test": True})


class AdvisoryNotificationTests(unittest.TestCase):
    def setUp(self):
        self.thresholds = IrrigationThresholds(30, 40, 20, 30)
        self.farm = AdvisoryEvaluationInput(
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
        )
        self.weather = WeatherData(15, 27, 70)

    def test_sends_actionable_advisory(self):
        sender = FakeSmsSender()

        result = evaluate_and_send_advisory(
            self.farm,
            self.weather,
            self.thresholds,
            "+256779330159",
            sender,
        )

        self.assertEqual(result.evaluation.advisory.severity, "WARNING")
        self.assertIn("Irrigation is recommended", result.message)
        self.assertEqual(sender.sent[0][0], "+256779330159")
        self.assertEqual(result.delivery.status, "Success")

    def test_does_not_send_info_advisory(self):
        sender = FakeSmsSender()
        normal_farm = self.farm.__class__(
            farm_id="FARM001",
            crop="maize",
            soil_moisture=60,
            soil_ph=6.4,
            temperature=27.8,
            humidity=71.2,
            rain_detected=False,
            water_level=78,
            location="Kampala",
            growth_stage="vegetative",
        )

        result = evaluate_and_send_advisory(
            normal_farm,
            self.weather,
            self.thresholds,
            "+256779330159",
            sender,
        )

        self.assertEqual(result.evaluation.advisory.severity, "INFO")
        self.assertIsNone(result.message)
        self.assertIsNone(result.delivery)
        self.assertEqual(sender.sent, [])
