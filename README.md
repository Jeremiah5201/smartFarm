# SMARTFARM PROJECT

This repository contains the four-member SmartFarm project.

## Main components

- `esp32/` — Member 1: Cirkit Designer, ESP32 firmware, sensors and MQTT.
- `backend/` — Members 2 and 3: MQTT ingestion, database, APIs, intelligence, weather and SMS.
- `frontend/` — Member 4: web dashboard.
- `docs/` — shared integration and testing documentation.
- `database/` — migrations and seed data.

Read `SMARTFARM_INTEGRATION_SPEC.md` before writing integration code.

## System flow

Cirkit Designer → ESP32 → HiveMQ → Backend → Database/Decision Engine → Frontend + SMS

The irrigation feedback path is:

Backend → HiveMQ → ESP32 → Virtual Pump
