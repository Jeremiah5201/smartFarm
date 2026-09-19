# MQTT Topics

The backend subscribes to `smartfarm/+/telemetry` with QoS 1. The `+` wildcard
captures the farm ID and the message body must follow the canonical telemetry
contract. The backend publishes actuator commands with QoS 1.

| Topic | Publisher | Backend behavior |
|---|---|---|
| `smartfarm/{farm_id}/telemetry` | ESP32 | Validate and store a sensor reading |
| `smartfarm/{farm_id}/status` | ESP32 | Reserved for device monitoring |
| `smartfarm/{farm_id}/command` | Intelligence service | Reserved for ESP32 commands |
| `smartfarm/{farm_id}/advisory` | Intelligence service | Reserved for dashboard/monitoring |

Malformed JSON, missing fields, invalid physical ranges, and a device ID that
does not match the farm's registered device are rejected and are not stored.

Every pump-on command includes a finite `duration_sec` fail-safe value.
