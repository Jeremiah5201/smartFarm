import unittest

from app.intelligence.crop_advisor import (
    CropAdvisoryInput,
    generate_crop_advisory,
)
from app.intelligence.irrigation_engine import IrrigationDecision


class CropAdvisorTests(unittest.TestCase):
    def test_generates_explainable_irrigation_advisory(self):
        advisory = generate_crop_advisory(
            CropAdvisoryInput(
                "maize", 6.4, 25, 27.8, 71.2, "Kampala", "flowering"
            ),
            IrrigationDecision(
                irrigation_required=True,
                pump=True,
                duration_seconds=30,
                reason="Low soil moisture and low rain probability.",
            ),
        )

        self.assertEqual(advisory.status, "Needs attention")
        self.assertEqual(advisory.severity, "WARNING")
        self.assertEqual(advisory.advisory_type, "IRRIGATION")
        self.assertIn("maize", advisory.message)
        self.assertTrue(advisory.reason)

    def test_generates_info_advisory_when_irrigation_is_not_required(self):
        advisory = generate_crop_advisory(
            CropAdvisoryInput(
                "maize", 6.4, 60, 27.8, 71.2, "Kampala", "vegetative"
            ),
            IrrigationDecision(
                irrigation_required=False,
                pump=False,
                duration_seconds=0,
                reason="Soil moisture is at or above the configured threshold.",
            ),
        )

        self.assertEqual(advisory.status, "Suitable")
        self.assertEqual(advisory.severity, "INFO")
        self.assertEqual(advisory.advisory_type, "CROP_CONDITION")

    def test_supports_all_project_crops(self):
        for crop in ("maize", "rice", "groundnuts", "beans", "millets", "soybeans"):
            with self.subTest(crop=crop):
                advisory = generate_crop_advisory(
                    CropAdvisoryInput(crop, 6.2, 60, 27, 70, "Kampala", "vegetative"),
                    IrrigationDecision(False, False, 0, "No irrigation required."),
                )
                self.assertEqual(advisory.status, "Suitable")

    def test_flags_ph_outside_crop_screening_range(self):
        advisory = generate_crop_advisory(
            CropAdvisoryInput("soybean", 5.0, 60, 27, 70, "Kampala", "vegetative"),
            IrrigationDecision(False, False, 0, "No irrigation required."),
        )

        self.assertEqual(advisory.status, "Needs attention")
        self.assertEqual(advisory.severity, "WARNING")
        self.assertIn("pH", advisory.reason)

    def test_requires_location_and_growth_stage_for_numeric_advice(self):
        advisory = generate_crop_advisory(
            CropAdvisoryInput("rice", 6.0, 60, 27, 70),
            IrrigationDecision(False, False, 0, "No irrigation required."),
        )

        self.assertEqual(advisory.status, "Conditionally suitable")
        self.assertIn("Location and crop growth stage", advisory.reason)

    def test_rejects_unknown_crop(self):
        with self.assertRaisesRegex(ValueError, "unsupported crop"):
            generate_crop_advisory(
                CropAdvisoryInput("unknown", 6.0, 60, 27, 70),
                IrrigationDecision(False, False, 0, "No irrigation required."),
            )


if __name__ == "__main__":
    unittest.main()
