import unittest

from app.intelligence.crop_advisor import CropAdvisory
from app.intelligence.irrigation_engine import IrrigationInput
from app.services.sms import AfricasTalkingSmsClient, format_advisory_sms


class SmsTests(unittest.TestCase):
    def test_sends_through_africas_talking_response(self):
        captured = {}

        def fake_post(url, form, headers, timeout):
            captured["url"] = url
            captured["form"] = form
            captured["headers"] = headers
            captured["timeout"] = timeout
            return (
                b'{"SMSMessageData":{"Recipients":[{"status":"Success",'
                b'"messageId":"ATX-001"}]}}'
            )

        client = AfricasTalkingSmsClient(
            "sandbox",
            "test-key",
            "SMARTFARM",
            http_post=fake_post,
        )
        result = client.send("+256700000000", "Test SmartFarm message")

        self.assertEqual(result.status, "Success")
        self.assertEqual(result.message_id, "ATX-001")
        self.assertEqual(captured["form"]["username"], "sandbox")
        self.assertEqual(captured["form"]["to"], "+256700000000")
        self.assertEqual(captured["form"]["from"], "SMARTFARM")
        self.assertEqual(captured["headers"]["Content-Type"], "application/x-www-form-urlencoded")
        self.assertEqual(captured["timeout"], 15)

    def test_rejects_invalid_provider_response(self):
        def fake_post(*args):
            if len(args) != 4:
                raise AssertionError("unexpected SMS transport arguments")
            return b"not-json"

        client = AfricasTalkingSmsClient(
            "sandbox",
            "test-key",
            http_post=fake_post,
        )

        with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
            client.send("+256700000000", "Test")

    def test_formats_farmer_facing_message(self):
        message = format_advisory_sms(
            "maize",
            IrrigationInput(25, False, 15, 78),
            6.4,
            CropAdvisory(
                "Needs attention",
                "WARNING",
                "IRRIGATION",
                "Irrigate your maize field if water is available.",
                "Low soil moisture.",
            ),
        )

        self.assertIn("Soil moisture: 25%", message)
        self.assertIn("pH: 6.4", message)
        self.assertIn("Rain probability: 15%", message)
        self.assertIn("Irrigate your maize field", message)
        self.assertNotIn("smartfarm/", message)
        self.assertNotIn("MQTT", message)

    def test_handles_unknown_forecast(self):
        message = format_advisory_sms(
            "maize",
            IrrigationInput(25, False, None, 78),
            6.4,
            CropAdvisory(
                "Needs attention",
                "WARNING",
                "IRRIGATION",
                "Check the field.",
                "Forecast unavailable.",
            ),
        )

        self.assertIn("Rain probability: unknown", message)
