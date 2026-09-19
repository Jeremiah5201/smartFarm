# SmartFarm Dashboard

Member 4's dashboard consumes the backend REST API. It does not connect to
the ESP32 or MQTT directly.

## Run locally

From `frontend/`:

```text
npm install
npm run dev
```

The Vite development server proxies `/api` requests to
`http://localhost:8000`. Start the FastAPI backend first, then open
`http://localhost:5173`.

Available dashboard data:

- Farm selection and device status
- Live sensor cards
- Recent telemetry table
- Irrigation state and history
- Manual irrigation override with a finite duration

Advisory, weather, and SMS panels remain reserved for Member 3's future API
endpoints and are clearly marked as not connected until those routes exist.
# Frontend

Owner: Member 4.

Consume the agreed REST APIs. Do not create an independent sensor-data contract.
