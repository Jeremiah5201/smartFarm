import unittest

from app.intelligence.irrigation_engine import (
    IrrigationInput,
    IrrigationThresholds,
    decide_irrigation,
)


class IrrigationEngineTests(unittest.TestCase):
    def setUp(self):
        self.thresholds = IrrigationThresholds(
            soil_moisture_threshold=30,
            forecast_rain_probability_threshold=40,
            minimum_water_level=20,
            duration_seconds=30,
        )

    def test_recommends_irrigation_when_all_conditions_are_met(self):
        result = decide_irrigation(
            IrrigationInput(
                soil_moisture=25,
                rain_detected=False,
                forecast_rain_probability=15,
                water_level=78,
            ),
            self.thresholds,
        )

        self.assertTrue(result.irrigation_required)
        self.assertTrue(result.pump)
        self.assertEqual(result.duration_seconds, 30)

    def test_does_not_recommend_irrigation_when_a_condition_is_not_met(self):
        readings = [
            IrrigationInput(35, False, 15, 78),
            IrrigationInput(25, True, 15, 78),
            IrrigationInput(25, False, 60, 78),
            IrrigationInput(25, False, 15, 20),
            IrrigationInput(25, False, None, 78),
        ]

        for reading in readings:
            with self.subTest(reading=reading):
                result = decide_irrigation(reading, self.thresholds)

                self.assertFalse(result.irrigation_required)
                self.assertFalse(result.pump)
                self.assertEqual(result.duration_seconds, 0)
                self.assertTrue(result.reason)

    def test_rejects_invalid_forecast_probability(self):
        with self.assertRaisesRegex(ValueError, "forecast_rain_probability"):
            decide_irrigation(
                IrrigationInput(25, False, 101, 78),
                self.thresholds,
            )


if __name__ == "__main__":
    unittest.main()

