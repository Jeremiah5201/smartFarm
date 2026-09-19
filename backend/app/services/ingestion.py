from sqlalchemy.orm import Session

from app.api.schemas import TelemetryPayload
from app.database.models import Farm, SensorReading


def save_telemetry(db: Session, farm_id: str, payload: TelemetryPayload) -> SensorReading:
    farm = db.get(Farm, farm_id)
    if farm is None:
        farm = Farm(farm_id=farm_id, farm_name=farm_id, device_id=payload.device_id)
        db.add(farm)
        db.flush()
    elif farm.device_id != payload.device_id:
        raise ValueError("device_id does not belong to this farm")

    reading = SensorReading(farm_id=farm_id, **payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading