# API Specification

The Member 2 service runs at `http://localhost:8000` and provides automatic
OpenAPI documentation at `/docs`.

## Core endpoints

- `GET /api/health` checks the service and database.
- `GET /api/farms` lists registered farms.
- `POST /api/farms` creates a farm. The initial `farm_id` is the `device_id`.
- `GET /api/farms/{farm_id}` returns one farm.
- `POST /api/farms/{farm_id}/telemetry` validates and stores one reading.
- `GET /api/farms/{farm_id}/latest` returns the newest reading.
- `GET /api/farms/{farm_id}/readings?limit=50` returns recent readings.
- `GET /api/irrigation/{farm_id}/history?limit=50` returns irrigation events.
- `POST /api/irrigation/{farm_id}/override` records and publishes a manual command.

Manual command example:

```json
{
	"pump": true,
	"duration_sec": 45,
	"reason": "Operator confirmed dry soil",
	"force_override": false
}
```

Example telemetry request:

```json
{
	"device_id": "FARM001",
	"timestamp": "2026-09-19T10:00:00Z",
	"soil_moisture": 32.5,
	"soil_ph": 6.4,
	"temperature": 27.8,
	"humidity": 71.2,
	"light": 65.0,
	"rain_detected": false,
	"water_level": 78.0,
	"pump_status": false
}
```

Intelligence examples:
- GET `/api/farms/{farm_id}/advisory`
- GET `/api/farms/{farm_id}/irrigation`
- GET `/api/farms/{farm_id}/weather`
- GET `/api/farms/{farm_id}/sms-history`
