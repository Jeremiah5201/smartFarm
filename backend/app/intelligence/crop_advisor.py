"""Conservative, explainable crop screening advice for SmartFarm.

The ranges in this module are broad screening ranges, not prescriptions.
Local cultivar, soil texture, drainage, altitude, climate, and growth stage
must be considered before a farmer makes a management decision.
"""

from dataclasses import dataclass
from typing import Literal

from .irrigation_engine import IrrigationDecision

AdvisorySeverity = Literal["INFO", "WARNING", "CRITICAL"]
AdvisoryStatus = Literal["Suitable", "Conditionally suitable", "Needs attention"]


@dataclass(frozen=True)
class CropProfile:
    """Conservative screening ranges assembled from agronomy references."""

    name: str
    ph_min: float
    ph_max: float
    temperature_min: float
    temperature_max: float
    critical_stages: tuple[str, ...]


CROP_PROFILES = {
    "maize": CropProfile("maize", 5.5, 7.0, 18.0, 32.0, ("flowering", "grain_fill")),
    "rice": CropProfile("rice", 5.0, 6.5, 20.0, 35.0, ("establishment", "flowering")),
    "groundnuts": CropProfile(
        "groundnuts", 5.5, 6.5, 22.0, 30.0, ("flowering", "pegging", "pod_fill")
    ),
    "beans": CropProfile("beans", 5.5, 6.5, 18.0, 30.0, ("flowering", "pod_fill")),
    "millets": CropProfile(
        "millets", 5.5, 7.5, 20.0, 35.0, ("establishment", "flowering", "grain_fill")
    ),
    "soybeans": CropProfile(
        "soybeans", 6.0, 7.0, 20.0, 30.0, ("flowering", "pod_fill")
    ),
}

CROP_ALIASES = {
    "corn": "maize",
    "groundnut": "groundnuts",
    "peanut": "groundnuts",
    "common bean": "beans",
    "bean": "beans",
    "millet": "millets",
    "soybean": "soybeans",
    "soya bean": "soybeans",
    "soya beans": "soybeans",
}


@dataclass(frozen=True)
class CropAdvisoryInput:
    """Farm and environmental values used to create an advisory."""

    crop: str
    soil_ph: float
    soil_moisture: float
    temperature: float
    humidity: float
    location: str = ""
    growth_stage: str = "unknown"


@dataclass(frozen=True)
class CropAdvisory:
    """Explainable advisory result."""

    status: AdvisoryStatus
    severity: AdvisorySeverity
    advisory_type: str
    message: str
    reason: str


def generate_crop_advisory(
    reading: CropAdvisoryInput,
    irrigation: IrrigationDecision,
) -> CropAdvisory:
    """Generate conservative crop screening and irrigation advice."""

    crop_input = reading.crop.strip().lower()
    if not crop_input:
        raise ValueError("crop must not be empty")
    crop_key = CROP_ALIASES.get(crop_input, crop_input)
    profile = CROP_PROFILES.get(crop_key)
    if profile is None:
        raise ValueError(
            f"unsupported crop {reading.crop!r}; supported crops: "
            f"{', '.join(sorted(CROP_PROFILES))}"
        )
    if not 0 <= reading.soil_moisture <= 100:
        raise ValueError("soil_moisture must be between 0 and 100")
    if not 0 <= reading.humidity <= 100:
        raise ValueError("humidity must be between 0 and 100")

    issues: list[str] = []
    if not profile.ph_min <= reading.soil_ph <= profile.ph_max:
        issues.append(
            f"Soil pH {reading.soil_ph:g} is outside the broad "
            f"{profile.ph_min:g}-{profile.ph_max:g} screening range for {profile.name}."
        )
    if not profile.temperature_min <= reading.temperature <= profile.temperature_max:
        issues.append(
            f"Temperature {reading.temperature:g}°C is outside the broad "
            f"{profile.temperature_min:g}-{profile.temperature_max:g}°C "
            f"screening range for {profile.name}."
        )

    location = reading.location.strip()
    growth_stage = reading.growth_stage.strip().lower()
    if not location or not growth_stage or growth_stage == "unknown":
        issues.append(
            "Location and crop growth stage are required before giving "
            "site-specific numeric advice."
        )

    if irrigation.irrigation_required:
        stage_note = ""
        if growth_stage in profile.critical_stages:
            stage_note = (
                f" Moisture management is especially important during {growth_stage}."
            )
        return CropAdvisory(
            status="Needs attention",
            severity=(
                "CRITICAL"
                if any("outside the broad" in issue for issue in issues)
                else "WARNING"
            ),
            advisory_type="IRRIGATION",
            message=(
                f"Soil moisture is low for the {profile.name} field. "
                "Irrigation is recommended if water is available."
                f"{stage_note}"
            ),
            reason=" ".join([irrigation.reason, *issues]).strip(),
        )

    if issues:
        status: AdvisoryStatus = "Conditionally suitable"
        if any("outside the broad" in issue for issue in issues):
            status = "Needs attention"
        return CropAdvisory(
            status=status,
            severity="WARNING",
            advisory_type="CROP_CONDITION",
            message=(
                f"{profile.name.title()} conditions need review. "
                "Use local soil tests, weather, cultivar guidance, and growth stage "
                "before taking action."
            ),
            reason=" ".join(issues),
        )

    return CropAdvisory(
        status="Suitable",
        severity="INFO",
        advisory_type="CROP_CONDITION",
        message=(
            f"Current measured conditions are within broad screening ranges for "
            f"the {profile.name} field."
        ),
        reason=(
            "This is general screening guidance, not a site-specific agronomic "
            "prescription."
        ),
    )
