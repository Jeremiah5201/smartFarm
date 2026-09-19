import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.database.database import Base, engine
from app.main import app
from app.database.database import SessionLocal
from app.mqtt.subscriber import process_telemetry_message


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def payload():
    return {
        "device_id": "FARM001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "soil_moisture": 32.5,
        "soil_ph": 6.4,
        "temperature": 27.8,
        "humidity": 71.2,
        "light": 65.0,
        "rain_detected": False,
        "water_level": 78.0,
        "pump_status": False,
    }


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_telemetry_is_stored_and_returned():
    response = client.post("/api/farms/FARM001/telemetry", json=payload())
    assert response.status_code == 201
    assert response.json()["soil_moisture"] == 32.5

    latest = client.get("/api/farms/FARM001/latest")
    assert latest.status_code == 200
    assert latest.json()["device_id"] == "FARM001"


def test_invalid_percentage_is_rejected():
    data = payload()
    data["humidity"] = 101
    response = client.post("/api/farms/FARM002/telemetry", json=data)
    assert response.status_code == 422


def test_mqtt_payload_uses_the_same_validation_and_storage_path():
    db = SessionLocal()
    try:
        process_telemetry_message(db, "FARM003", json.dumps(payload()))
    finally:
        db.close()

    response = client.get("/api/farms/FARM003/latest")
    assert response.status_code == 200