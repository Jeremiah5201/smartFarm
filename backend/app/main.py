from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.farms import router as farms_router
from app.api.irrigation import router as irrigation_router
from app.database.database import Base, engine, get_db
from app.database import models  # noqa: F401
from app.config import settings
from app.database.database import SessionLocal
from app.mqtt.subscriber import TelemetrySubscriber
from app.services.irrigation import set_command_publisher

Base.metadata.create_all(bind=engine)
mqtt_service = TelemetrySubscriber(SessionLocal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.mqtt_enabled:
        mqtt_service.start_background()
        set_command_publisher(mqtt_service.publish_command)
    yield
    if settings.mqtt_enabled:
        mqtt_service.stop()

app = FastAPI(title="SmartFarm Backend", version="1.0.0", lifespan=lifespan)
app.include_router(farms_router)
app.include_router(irrigation_router)


@app.get("/api/health", tags=["system"])
def health():
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}