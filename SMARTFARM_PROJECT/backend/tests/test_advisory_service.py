import unittest

from app.intelligence.irrigation_engine import IrrigationThresholds
from app.intelligence.weather import WeatherData
from app.services.advisory import AdvisoryEvaluationInput, evaluate_farm


class AdvisoryServiceTests(unittest.TestCase):
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

    def test_combines_weather_and_sensor_data(self):
        evaluation = evaluate_farm(
            self.farm,
            WeatherData(rain_probability=15, temperature=27, humidity=70),
            self.thresholds,
        )

        self.assertEqual(evaluation.farm_id, "FARM001")
        self.assertTrue(evaluation.irrigation.irrigation_required)
        self.assertEqual(evaluation.advisory.severity, "WARNING")

    def test_missing_forecast_prevents_automatic_irrigation(self):
        evaluation = evaluate_farm(
            self.farm,
            WeatherData(rain_probability=None, temperature=27, humidity=70),
            self.thresholds,
        )

        self.assertFalse(evaluation.irrigation.irrigation_required)
        self.assertEqual(evaluation.advisory.severity, "INFO")

    def test_current_sensor_rain_overrides_low_forecast_probability(self):
        raining_farm = self.farm.__class__(
            farm_id=self.farm.farm_id,
            crop=self.farm.crop,
            soil_moisture=self.farm.soil_moisture,
            soil_ph=self.farm.soil_ph,
            temperature=self.farm.temperature,
            humidity=self.farm.humidity,
            rain_detected=True,
            water_level=self.farm.water_level,
            location=self.farm.location,
            growth_stage=self.farm.growth_stage,
        )

        evaluation = evaluate_farm(
            raining_farm,
            WeatherData(rain_probability=15, temperature=27, humidity=70),
            self.thresholds,
        )

        self.assertFalse(evaluation.irrigation.irrigation_required)
        self.assertIn("Rain has been detected", evaluation.irrigation.reason)

    def test_requires_farm_id(self):
        with self.assertRaisesRegex(ValueError, "farm_id"):
            evaluate_farm(
                self.farm.__class__(
                    farm_id=" ",
                    crop=self.farm.crop,
                    soil_moisture=self.farm.soil_moisture,
                    soil_ph=self.farm.soil_ph,
                    temperature=self.farm.temperature,
                    humidity=self.farm.humidity,
                    rain_detected=self.farm.rain_detected,
                    water_level=self.farm.water_level,
                ),
                WeatherData(15, 27, 70),
                self.thresholds,
            )
