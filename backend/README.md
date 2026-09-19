# SmartFarm Backend

This service implements Member 2's boundary: MQTT telemetry ingestion, payload
validation, SQLite persistence, and the core REST API. Intelligence, weather,
irrigation rules, and SMS remain separate Member 3 responsibilities.

## Local setup

From this directory:

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the interactive API documentation.

Initialize the database explicitly when needed:

```text
python -m app.database.init_db
```

The local default uses SQLite and does not require HiveMQ. Set `MQTT_ENABLED=true`
and provide broker settings in `.env` when the broker is available.

The shared `.env.example` is prefilled with the HiveMQ host, TLS port, and
username supplied by the team. Replace only `MQTT_PASSWORD` in your local
untracked `.env` file. Never commit that file.

The FastAPI application starts the MQTT subscriber automatically when
`MQTT_ENABLED=true`.

Core irrigation endpoints:

- `GET /api/irrigation/{farm_id}/history?limit=50`
- `POST /api/irrigation/{farm_id}/override`

Pump-on commands require a finite `duration_sec` between 1 and 3600 seconds.

## First telemetry request

```text
POST /api/farms/FARM001/telemetry
```

Use the canonical JSON payload in `docs/api/api-spec.md`. The same ingestion
function is used by this endpoint and the MQTT subscriber.
