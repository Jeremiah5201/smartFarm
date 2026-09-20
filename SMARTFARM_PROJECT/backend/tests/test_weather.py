import unittest

from app.intelligence.weather import (
    WeatherData,
    fetch_open_meteo_weather,
    normalize_weather_response,
)


class WeatherTests(unittest.TestCase):
    def test_normalizes_valid_response(self):
        weather = normalize_weather_response(
            {"rain_probability": 15, "temperature": 27, "humidity": 70}
        )

        self.assertEqual(
            weather,
            WeatherData(rain_probability=15, temperature=27, humidity=70),
        )

    def test_allows_missing_rain_probability(self):
        weather = normalize_weather_response({"temperature": 27})

        self.assertIsNone(weather.rain_probability)

    def test_rejects_invalid_probability(self):
        with self.assertRaisesRegex(ValueError, "rain_probability"):
            normalize_weather_response({"rain_probability": 101})

    def test_rejects_non_numeric_values(self):
        with self.assertRaisesRegex(ValueError, "temperature"):
            normalize_weather_response({"temperature": "warm"})

    def test_fetches_open_meteo_forecast(self):
        def fake_get(url, timeout):
            self.assertIn("precipitation_probability", url)
            self.assertEqual(timeout, 10)
            return {
                "hourly": {
                    "time": ["2099-01-01T00:00", "2099-01-01T01:00"],
                    "precipitation_probability": [15, 80],
                    "temperature_2m": [27, 28],
                    "relative_humidity_2m": [70, 71],
                }
            }

        weather = fetch_open_meteo_weather(
            0.3476,
            32.5825,
            http_get=fake_get,
        )

        self.assertEqual(weather, WeatherData(15, 27, 70))

    def test_rejects_malformed_open_meteo_response(self):
        with self.assertRaisesRegex(ValueError, "hourly"):
            def fake_get(*args):
                self.assertEqual(len(args), 2)
                return {}

            fetch_open_meteo_weather(
                0,
                0,
                http_get=fake_get,
            )
