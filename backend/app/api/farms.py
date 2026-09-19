from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.schemas import FarmCreate, FarmResponse, ReadingResponse, TelemetryPayload
from app.database.database import get_db
from app.database.models import Farm, SensorReading
from app.services.ingestion import save_telemetry

router = APIRouter(prefix="/api/farms", tags=["farms"])


@router.get("", response_model=list[FarmResponse])
def list_farms(db: Session = Depends(get_db)):
    return list(db.scalars(select(Farm).order_by(Farm.farm_id)))


@router.post("/{farm_id}/telemetry", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED)
def receive_telemetry(farm_id: str, payload: TelemetryPayload, db: Session = Depends(get_db)):
    try:
        reading = save_telemetry(db, farm_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {**payload.model_dump(), "farm_id": reading.farm_id}


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="farm not found")
    return farm


def _readings(db: Session, farm_id: str, limit: int):
    if db.get(Farm, farm_id) is None:
        raise HTTPException(status_code=404, detail="farm not found")
    return list(db.scalars(select(SensorReading).where(SensorReading.farm_id == farm_id).order_by(desc(SensorReading.timestamp)).limit(limit)))


@router.get("/{farm_id}/latest", response_model=ReadingResponse)
def latest_reading(farm_id: str, db: Session = Depends(get_db)):
    readings = _readings(db, farm_id, 1)
    if not readings:
        raise HTTPException(status_code=404, detail="no readings found")
    reading = readings[0]
    return {**reading.__dict__, "farm_id": farm_id}


@router.get("/{farm_id}/readings", response_model=list[ReadingResponse])
def readings(farm_id: str, limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    return _readings(db, farm_id, limit)


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(payload: FarmCreate, db: Session = Depends(get_db)):
    if db.get(Farm, payload.farm_id) is not None:
        raise HTTPException(status_code=409, detail="farm already exists")
    farm = Farm(**payload.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm