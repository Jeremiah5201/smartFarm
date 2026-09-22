import unittest

from app.intelligence.irrigation_engine import IrrigationDecision
from app.services.irrigation_commands import build_irrigation_command


class IrrigationCommandTests(unittest.TestCase):
    def test_builds_agreed_command(self):
        command = build_irrigation_command(
            "FARM001",
            IrrigationDecision(True, True, 30, "Low soil moisture."),
        )

        self.assertIsNotNone(command)
        topic, payload = command
        self.assertEqual(topic, "smartfarm/FARM001/command")
        self.assertEqual(payload["command"], "IRRIGATION")
        self.assertTrue(payload["pump"])
        self.assertEqual(payload["duration_seconds"], 30)

    def test_does_not_build_command_when_irrigation_is_not_required(self):
        command = build_irrigation_command(
            "FARM001",
            IrrigationDecision(False, False, 0, "Rain detected."),
        )

        self.assertIsNone(command)
