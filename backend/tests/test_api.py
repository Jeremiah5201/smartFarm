import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.database.database import Base, engine
from app.main import app
from app.database.database import SessionLocal
from app.mqtt.subscriber import process_telemetry_message
from app.services.irrigation import create_irrigation_event
from app.api.schemas import IrrigationOverride


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


def test_guide_telemetry_accepts_rain_field_without_pump_status():
    data = payload()
    data["rain"] = data.pop("rain_detected")
    data.pop("pump_status")
    response = client.post("/api/farms/FARM004/telemetry", json=data)
    assert response.status_code == 201
    assert response.json()["rain_detected"] is False


def test_telemetry_without_device_timestamp_uses_ingestion_time():
    data = payload()
    data.pop("timestamp")
    response = client.post("/api/farms/FARM005/telemetry", json=data)
    assert response.status_code == 201
    assert response.json()["timestamp"]


def test_mqtt_payload_uses_the_same_validation_and_storage_path():
    db = SessionLocal()
    try:
        process_telemetry_message(db, "FARM003", json.dumps(payload()))
    finally:
        db.close()

    response = client.get("/api/farms/FARM003/latest")
    assert response.status_code == 200


def test_irrigation_override_is_recorded():
    response = client.post(
        "/api/irrigation/FARM001/override",
        json={"pump": True, "duration_sec": 45, "reason": "Manual test"},
    )
    assert response.status_code == 201
    assert response.json()["duration_sec"] == 45

    history = client.get("/api/irrigation/FARM001/history")
    assert history.status_code == 200
    assert history.json()[0]["pump_status"] is True


def test_pump_override_requires_a_finite_duration():
    response = client.post(
        "/api/irrigation/FARM001/override",
        json={"pump": True, "duration_sec": 0, "reason": "Unsafe"},
    )
    assert response.status_code == 422


def test_dashboard_intelligence_routes_return_contracts():
    advisory = client.get("/api/farms/FARM001/advisory")
    assert advisory.status_code == 200
    assert advisory.json()[0]["severity"] in {"INFO", "WARNING", "CRITICAL"}

    weather = client.get("/api/farms/FARM001/weather")
    assert weather.status_code == 200
    assert weather.json()["source"] == "field telemetry"

    sms_history = client.get("/api/farms/FARM001/sms-history")
    assert sms_history.status_code == 200
    assert sms_history.json() == []


def test_irrigation_service_calls_command_publisher():
    published = []
    db = SessionLocal()
    try:
        create_irrigation_event(
            db,
            "FARM001",
            IrrigationOverride(pump=True, duration_sec=30, reason="Test"),
            lambda farm_id, command_id, command: published.append((farm_id, command_id, command.duration_sec)),
        )
    finally:
        db.close()
    assert published[0][0] == "FARM001"
    assert published[0][2] == 30