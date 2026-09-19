from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field, field_validator


def percentage(value: float) -> float:
    if not 0 <= value <= 100:
        raise ValueError("must be between 0 and 100")
    return value


class TelemetryPayload(BaseModel):
    device_id: str = Field(min_length=1, max_length=50)
    timestamp: datetime
    soil_moisture: float
    soil_ph: float = Field(ge=0, le=14)
    temperature: float = Field(ge=-50, le=80)
    humidity: float
    light: float
    rain_detected: bool = Field(
        default=False,
        validation_alias=AliasChoices("rain_detected", "rain"),
    )
    water_level: float
    pump_status: bool = False

    _humidity_range = field_validator("soil_moisture", "humidity", "light", "water_level")(percentage)


class FarmCreate(BaseModel):
    farm_id: str = Field(min_length=1, max_length=50)
    farm_name: str = Field(min_length=1, max_length=120)
    device_id: str = Field(min_length=1, max_length=50)
    farmer_id: int | None = None
    location: str | None = None
    crop: str | None = None


class FarmResponse(FarmCreate):
    farm_id: str

    model_config = {"from_attributes": True}


class ReadingResponse(TelemetryPayload):
    farm_id: str


class HealthResponse(BaseModel):
    status: str
    database: str


class IrrigationOverride(BaseModel):
    pump: bool
    duration_sec: int = Field(ge=1, le=3600)
    reason: str = Field(min_length=1, max_length=500)
    force_override: bool = False

    @field_validator("duration_sec")
    @classmethod
    def duration_required_for_pump(cls, value: int, info):
        if info.data.get("pump") is True and value <= 0:
            raise ValueError("duration_sec must be positive when pump is enabled")
        return value


class IrrigationEventResponse(BaseModel):
    farm_id: str
    timestamp: datetime
    duration_sec: int
    reason: str
    pump_status: bool
    command_id: str | None

    model_config = {"from_attributes": True}