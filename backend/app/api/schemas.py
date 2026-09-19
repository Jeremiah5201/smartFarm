from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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
    rain_detected: bool
    water_level: float
    pump_status: bool

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