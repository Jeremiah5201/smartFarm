from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.api.schemas import IrrigationOverride
from app.database.models import Farm, IrrigationEvent

command_publisher = lambda farm_id, command_id, command: None


def set_command_publisher(publisher) -> None:
    global command_publisher
    command_publisher = publisher


def get_command_publisher():
    return command_publisher


def create_irrigation_event(
    db: Session,
    farm_id: str,
    command: IrrigationOverride,
    publish_command,
) -> IrrigationEvent:
    if db.get(Farm, farm_id) is None:
        raise ValueError("farm not found")

    command_id = f"CMD_{uuid4().hex[:10]}"
    event = IrrigationEvent(
        farm_id=farm_id,
        timestamp=datetime.now(timezone.utc),
        duration_seconds=command.duration_sec,
        reason=command.reason,
        pump_status=command.pump,
        command_id=command_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    publish_command(farm_id, command_id, command)
    return event