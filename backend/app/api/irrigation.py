from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.schemas import IrrigationEventResponse, IrrigationOverride
from app.database.database import get_db
from app.database.models import IrrigationEvent
from app.services.irrigation import create_irrigation_event, get_command_publisher

router = APIRouter(prefix="/api/irrigation", tags=["irrigation"])


@router.get("/{farm_id}/history", response_model=list[IrrigationEventResponse])
def irrigation_history(
    farm_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(IrrigationEvent)
            .where(IrrigationEvent.farm_id == farm_id)
            .order_by(desc(IrrigationEvent.timestamp))
            .limit(limit)
        )
    )


@router.post("/{farm_id}/override", response_model=IrrigationEventResponse, status_code=201)
def irrigation_override(
    farm_id: str,
    command: IrrigationOverride,
    db: Session = Depends(get_db),
):
    try:
        return create_irrigation_event(db, farm_id, command, get_command_publisher())
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error