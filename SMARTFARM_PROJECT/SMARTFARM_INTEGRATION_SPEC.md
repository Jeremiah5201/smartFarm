# SMARTFARM Integration Specification

**Project:** SmartFarm – IoT-Based Soil Intelligence, Smart Irrigation and Prescriptive Crop Advisory via SMS  
**Team size:** 4 members  
**Primary simulation platform:** Cirkit Designer  
**IoT communication:** MQTT via HiveMQ  
**Backend:** Python-based services/API  
**Frontend:** Web dashboard  
**Farmer communication:** SMS  
**Document status:** Team Integration Contract – Version 1.0

---

## 1. Purpose of this document

This document is the integration contract for the four-member SmartFarm project.

Its purpose is to make sure that all members build compatible components. Each member owns a defined part of the system, while the interfaces between the parts are agreed in advance.

**Golden rule:**

> The ESP32 team defines and publishes the agreed sensor-data contract → the backend ingestion team receives and stores that contract → the intelligence/SMS team processes the stored data → the frontend team consumes the agreed backend API.

No member should independently change MQTT topics, JSON field names, units, API response structures, or database contracts without informing the rest of the team.

---

# 2. Project objective

SmartFarm is an IoT-based agricultural decision-support system intended to:

1. Collect soil and environmental information.
2. Process selected measurements at the ESP32 edge.
3. Transmit sensor data using MQTT.
4. Receive and store sensor data in a backend.
5. Combine field measurements with weather information.
6. Determine whether irrigation is required.
7. Generate prescriptive crop and soil-management advice.
8. Display farm information through a web dashboard.
9. Deliver important recommendations through SMS so that farmers can receive advice without smartphones.

The field hardware is simulated rather than physically deployed during the development stage.

---

# 3. Complete project flow

```text
┌───────────────────────────────────────────────────────────────┐
│                    CIRKIT DESIGNER                            │
│                                                               │
│  ESP32 + simulated agricultural sensors                      │
│                                                               │
│  Soil Moisture | Soil pH | Temperature | Humidity             │
│  Light | Rain | Water Tank Level | Relay/Pump                │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               │ Wi-Fi / MQTT
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                         HIVEMQ                                │
│                       MQTT BROKER                             │
│                                                               │
│ smartfarm/{farm_id}/telemetry                                │
│ smartfarm/{farm_id}/command                                  │
│ smartfarm/{farm_id}/status                                   │
│ smartfarm/{farm_id}/advisory                                 │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               │ MQTT Subscribe
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                    BACKEND MEMBER 2                           │
│                  DATA / MQTT SERVICE                          │
│                                                               │
│ MQTT Subscriber → Validation → Database → REST API            │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                    BACKEND MEMBER 3                           │
│              INTELLIGENCE / WEATHER / SMS                    │
│                                                               │
│ Soil analysis + Weather + Crop rules                          │
│                ↓                                              │
│ Irrigation decision + Prescriptive advisory                   │
│                ↓                                              │
│ SMS generation / irrigation command                           │
└──────────────────────┬───────────────────┬────────────────────┘
                       │                   │
                       │ REST API          │ MQTT command
                       ▼                   ▼
             ┌──────────────────┐     ┌───────────────┐
             │ FRONTEND MEMBER 4│     │ ESP32 / PUMP  │
             │ Web Dashboard     │     │ Simulation    │
             └──────────────────┘     └───────────────┘
                       │
                       ▼
                Farmer / User
                       │
                       ▼
                 SMS message
```

---

# 4. Team member boundaries

## Member 1 – ESP32 / IoT / Hardware Simulation

### Owns

- Cirkit Designer circuit.
- ESP32 configuration.
- Sensor connections.
- MicroPython firmware if supported by the selected simulation environment.
- Sensor reading and conversion.
- Basic edge processing.
- MQTT publishing.
- MQTT command subscription.
- Relay/pump simulation.
- ESP32 testing.

### Does NOT own

- Database implementation.
- REST API implementation.
- Weather API integration.
- Crop advisory engine.
- SMS gateway.
- Frontend dashboard.

### Boundary

```text
Sensors
  ↓
ESP32
  ↓
Sensor processing
  ↓
JSON
  ↓
MQTT
  ↓
HiveMQ
```

and, in the reverse direction:

```text
HiveMQ
  ↓
MQTT command
  ↓
ESP32
  ↓
Relay/Pump
```

### Required deliverables

- Cirkit Designer project.
- Final circuit diagram.
- Pin map.
- ESP32 firmware.
- MQTT client implementation.
- Sensor payload examples.
- MQTT command handling.
- Pump/relay control.
- Hardware integration documentation.
- Hardware test evidence.

---

## Member 2 – Backend / MQTT / Database / REST API

### Owns

- MQTT subscriber service.
- MQTT message validation.
- Database.
- Farm/device records.
- Sensor readings.
- REST API.
- Backend configuration.
- API documentation.

### Does NOT own

- ESP32 firmware.
- Cirkit Designer circuit.
- Crop recommendation rules.
- SMS provider logic.
- Frontend UI.

### Boundary

```text
HiveMQ
  ↓
MQTT Subscriber
  ↓
JSON validation
  ↓
Database
  ↓
REST API
```

### Required deliverables

- Backend service.
- Database schema.
- MQTT subscriber.
- Sensor data persistence.
- REST endpoints.
- API documentation.
- Example API responses.
- Backend setup instructions.

---

## Member 3 – Backend Intelligence / Weather / SMS

### Owns

- Soil-condition analysis.
- Irrigation decision engine.
- Crop suitability/advisory rules.
- Weather integration.
- Advisory generation.
- SMS integration.
- Irrigation command generation.
- Advisory history.

### Does NOT own

- ESP32 hardware.
- Core MQTT ingestion service.
- Frontend UI.
- Changing the agreed sensor payload.

### Boundary

```text
Stored sensor data
       +
Weather information
       +
Crop requirements
       ↓
Decision engine
       ↓
Irrigation decision
Crop advisory
SMS advisory
       ↓
MQTT command / REST API
```

### Required deliverables

- Decision engine.
- Weather service.
- Crop rules.
- Advisory service.
- SMS service.
- Irrigation command service.
- API endpoints for recommendations.
- Test cases.

---

## Member 4 – Frontend

### Owns

- Web dashboard.
- Farm overview.
- Sensor visualization.
- Irrigation status.
- Weather display.
- Advisory display.
- SMS history display.
- Frontend API integration.
- UI/UX.

### Does NOT own

- ESP32 firmware.
- MQTT broker implementation.
- Database implementation.
- Core crop decision logic.
- SMS gateway implementation.

### Boundary

```text
Backend REST API
       ↓
Frontend
       ↓
Dashboard
```

The frontend should normally consume backend APIs rather than connecting directly to the ESP32.

---

# 5. Hardware specification

The initial simulated field device contains:

| Component | Purpose | Data |
|---|---|---|
| ESP32 | Main controller | Device control |
| Soil moisture sensor | Soil water status | % |
| DHT22 | Temperature/humidity | °C / % |
| Potentiometer | Simulated pH | pH |
| LDR | Light intensity | % |
| Rain sensor | Rain detection | boolean |
| Ultrasonic sensor | Water tank level | % |
| Relay | Pump switching | ON/OFF |
| Pump/LED | Irrigation representation | ON/OFF |
| OLED/LCD | Local display | Text |

The exact board model and firmware language must be confirmed against the selected Cirkit Designer simulation environment before the final firmware is frozen.

---

# 6. Proposed ESP32 pin map

The following is the team's initial proposal. Member 1 should verify pin availability in the selected ESP32 model and Cirkit Designer before finalizing.

| Component | Proposed GPIO | Type |
|---|---:|---|
| Soil moisture | GPIO 34 | Analog input |
| pH potentiometer | GPIO 35 | Analog input |
| LDR | GPIO 32 | Analog input |
| DHT22 | GPIO 4 | Digital |
| Rain sensor | GPIO 27 | Digital |
| Ultrasonic TRIG | GPIO 5 | Digital output |
| Ultrasonic ECHO | GPIO 18 | Digital input |
| Relay/Pump | GPIO 26 | Digital output |
| OLED SDA | GPIO 21 | I2C |
| OLED SCL | GPIO 22 | I2C |

If the final hardware configuration changes, update this section before other members integrate against it.

---

# 7. Sensor data contract

The agreed canonical field names are:

| Field | Type | Unit |
|---|---|---|
| device_id | string | - |
| timestamp | ISO-8601 string | UTC |
| soil_moisture | number | % |
| soil_ph | number | pH |
| temperature | number | °C |
| humidity | number | % |
| light | number | % |
| rain_detected | boolean | true/false |
| water_level | number | % |
| pump_status | boolean | true/false |

Do not rename fields without team agreement.

---

# 8. MQTT topic contract

Use the following topic structure:

```text
smartfarm/{farm_id}/telemetry
smartfarm/{farm_id}/status
smartfarm/{farm_id}/command
smartfarm/{farm_id}/advisory
```

Example:

```text
smartfarm/FARM001/telemetry
smartfarm/FARM001/status
smartfarm/FARM001/command
smartfarm/FARM001/advisory
```

## Topic ownership

| Topic | Publisher | Subscriber |
|---|---|---|
| telemetry | ESP32 | Backend |
| status | ESP32 | Backend / monitoring |
| command | Backend | ESP32 |
| advisory | Backend | Dashboard / monitoring |

---

# 9. Telemetry JSON contract

ESP32 publishes to:

```text
smartfarm/FARM001/telemetry
```

Example:

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

The backend must validate:

- Required fields exist.
- Numeric fields contain valid numbers.
- Boolean fields contain true/false.
- Values fall within agreed physical ranges.
- Timestamp is valid.

---

# 10. Irrigation command contract

Backend publishes to:

```text
smartfarm/FARM001/command
```

Example:

```json
{
  "command": "IRRIGATION",
  "pump": true,
  "duration_seconds": 30,
  "reason": "Low soil moisture and low rainfall probability"
}
```

ESP32 must respond by:

1. Receiving the MQTT command.
2. Validating the command.
3. Activating/deactivating the virtual pump.
4. Publishing updated status.
5. Recording the command locally in the serial log.

---

# 11. Device status contract

ESP32 may publish:

```text
smartfarm/FARM001/status
```

Example:

```json
{
  "device_id": "FARM001",
  "status": "ONLINE",
  "wifi_connected": true,
  "mqtt_connected": true,
  "pump_status": false
}
```

---

# 12. Advisory contract

Backend intelligence publishes an advisory such as:

```text
smartfarm/FARM001/advisory
```

Example:

```json
{
  "farm_id": "FARM001",
  "severity": "WARNING",
  "type": "IRRIGATION",
  "message": "Soil moisture is low. Irrigation is recommended if rainfall is not expected.",
  "created_at": "2026-09-19T10:05:00Z"
}
```

Suggested severity values:

```text
INFO
WARNING
CRITICAL
```

---

# 13. Database contract

## Farmer

```text
farmer_id
name
phone_number
location
preferred_language
```

## Farm

```text
farm_id
farmer_id
farm_name
location
crop
device_id
```

## SensorReading

```text
id
farm_id
device_id
timestamp
soil_moisture
soil_ph
temperature
humidity
light
rain_detected
water_level
pump_status
```

## IrrigationEvent

```text
id
farm_id
timestamp
pump_status
duration_seconds
reason
```

## Advisory

```text
id
farm_id
timestamp
severity
type
message
```

## SMSLog

```text
id
farmer_id
timestamp
phone_number
message
status
```

---

# 14. REST API contract

Member 2 owns the core data API.

Initial endpoints:

```text
GET /api/health

GET /api/farms

GET /api/farms/{farm_id}

GET /api/farms/{farm_id}/latest

GET /api/farms/{farm_id}/readings

GET /api/farms/{farm_id}/readings?limit=50
```

Member 3 adds intelligence endpoints:

```text
GET /api/farms/{farm_id}/advisory

GET /api/farms/{farm_id}/irrigation

GET /api/farms/{farm_id}/weather

GET /api/farms/{farm_id}/sms-history
```

The frontend team must consume these endpoints rather than inventing alternative data structures.

---

# 15. Example API response

For:

```text
GET /api/farms/FARM001/latest
```

the backend should return something similar to:

```json
{
  "farm_id": "FARM001",
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

---

# 16. Configuration management

Never commit passwords, API keys, MQTT credentials, or SMS credentials to GitHub.

Use environment variables.

Example `.env.example`:

```env
# Application
APP_ENV=development
APP_PORT=8000

# Database
DATABASE_URL=sqlite:///./smartfarm.db

# MQTT / HiveMQ
MQTT_HOST=your-hivemq-host
MQTT_PORT=8883
MQTT_USERNAME=your-username
MQTT_PASSWORD=your-password
MQTT_TLS=true

# MQTT topics
MQTT_TELEMETRY_TOPIC=smartfarm/{farm_id}/telemetry
MQTT_COMMAND_TOPIC=smartfarm/{farm_id}/command
MQTT_STATUS_TOPIC=smartfarm/{farm_id}/status
MQTT_ADVISORY_TOPIC=smartfarm/{farm_id}/advisory

# Weather
WEATHER_API_KEY=your-weather-api-key

# SMS
SMS_PROVIDER=your-provider
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=SMARTFARM

# Frontend
FRONTEND_URL=http://localhost:5173
```

Create a real `.env` locally, but commit only `.env.example`.

---

# 17. ESP32 configuration

Member 1 should maintain a configuration section containing:

```text
WIFI_SSID
WIFI_PASSWORD
MQTT_HOST
MQTT_PORT
MQTT_USERNAME
MQTT_PASSWORD
FARM_ID
DEVICE_ID
MQTT_TOPIC_TELEMETRY
MQTT_TOPIC_COMMAND
MQTT_TOPIC_STATUS
```

Credentials must not be hard-coded into public repository files.

---

# 18. Processing responsibilities

## ESP32 edge processing

ESP32 should:

- Read sensors.
- Convert raw sensor values into useful units.
- Perform basic validation.
- Determine basic local states such as dry/normal/wet.
- Control the virtual pump when commanded.
- Publish telemetry.

## Backend processing

Backend should:

- Validate incoming MQTT messages.
- Store sensor readings.
- Retrieve historical data.
- Combine sensor data with weather data.
- Apply crop advisory rules.
- Make the higher-level irrigation decision.
- Generate SMS messages.

This prevents too much application intelligence from being placed inside the ESP32 firmware.

---

# 19. Irrigation decision example

The initial rule engine can use:

```text
IF:
    soil_moisture < configured_threshold
AND:
    rain_detected == false
AND:
    forecast_rain_probability < configured_threshold
AND:
    water_level > minimum_water_level

THEN:
    irrigation_required = true
```

Otherwise:

```text
irrigation_required = false
```

These thresholds are configurable and must be documented. They are not universal agricultural recommendations.

---

# 20. Crop advisory

The first version should use a transparent rule-based approach rather than claiming machine-learning prediction.

Example inputs:

```text
soil pH
soil moisture
temperature
humidity
crop
weather
```

Example output:

```text
Suitable
Conditionally suitable
Needs attention
```

The advisory must explain the reason.

Example:

```text
Soil moisture is below the configured threshold.
Rain probability is low.
Irrigation is recommended.
```

---

# 21. SMS design

SMS should be short and actionable.

Example:

```text
SMARTFARM ALERT

Soil moisture: 28%
pH: 6.4
Rain probability: 15%

Recommendation:
Irrigate your maize field if water is available.
```

SMS should not expose technical MQTT information to the farmer.

---

# 22. Frontend requirements

The dashboard should show:

### Farm overview

- Farm name.
- Location.
- Current crop.
- Device status.

### Sensor cards

- Soil moisture.
- Soil pH.
- Temperature.
- Humidity.
- Light.
- Rain status.
- Water level.

### Irrigation

- Pump status.
- Last irrigation event.
- Irrigation recommendation.
- Reason.

### Weather

- Current/forecast information.
- Rain probability.

### Advisory

- Current recommendation.
- Severity.
- Date/time.

### SMS history

- Recipient.
- Message.
- Date/time.
- Delivery status.

---

# 23. Project folder structure

```text
SMARTFARM/
│
├── README.md
├── SMARTFARM_INTEGRATION_SPEC.md
├── .gitignore
├── .env.example
│
├── docs/
│   ├── architecture/
│   │   └── system-flow.md
│   ├── mqtt/
│   │   └── mqtt-topics.md
│   ├── api/
│   │   └── api-spec.md
│   ├── database/
│   │   └── database-schema.md
│   └── testing/
│       └── integration-test-plan.md
│
├── esp32/
│   ├── README.md
│   ├── firmware/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── sensors.py
│   │   ├── mqtt_client.py
│   │   └── irrigation.py
│   ├── circuit/
│   │   └── README.md
│   └── tests/
│       └── mqtt-payload-examples/
│
├── backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── mqtt/
│   │   │   └── subscriber.py
│   │   ├── api/
│   │   │   ├── farms.py
│   │   │   ├── sensors.py
│   │   │   ├── advisory.py
│   │   │   └── irrigation.py
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── intelligence/
│   │   │   ├── irrigation_engine.py
│   │   │   ├── crop_advisor.py
│   │   │   └── weather.py
│   │   └── services/
│   │       └── sms.py
│   └── tests/
│
├── frontend/
│   ├── README.md
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   └── tests/
│
└── database/
    ├── migrations/
    └── seed/
```

---

# 24. Git ownership

Recommended ownership:

```text
esp32/      → Member 1
backend/    → Members 2 and 3
frontend/   → Member 4
docs/       → All members
```

Every member should work on a separate branch:

```text
main

feature/esp32-iot
feature/backend-mqtt
feature/backend-intelligence
feature/frontend-dashboard
```

Changes should be merged into `main` only after testing.

---

# 25. Integration milestones

## Milestone 1 – Hardware

```text
ESP32 + sensors
       ↓
Serial readings
```

## Milestone 2 – MQTT

```text
ESP32
 ↓
HiveMQ
```

## Milestone 3 – Backend ingestion

```text
ESP32
 ↓
HiveMQ
 ↓
Backend
 ↓
Database
```

## Milestone 4 – Intelligence

```text
Database
 ↓
Decision engine
 ↓
Recommendation
```

## Milestone 5 – Frontend

```text
Backend API
 ↓
Dashboard
```

## Milestone 6 – SMS

```text
Recommendation
 ↓
SMS service
 ↓
Farmer
```

## Milestone 7 – Closed-loop irrigation

```text
Backend decision
 ↓
MQTT command
 ↓
ESP32
 ↓
Virtual pump
```

---

# 26. End-to-end integration test

The team must demonstrate this sequence:

```text
1. Start the Cirkit Designer ESP32 simulation.

2. Change a simulated sensor value.

3. ESP32 reads the new value.

4. ESP32 creates the agreed JSON payload.

5. ESP32 publishes the telemetry to HiveMQ.

6. Backend receives the MQTT message.

7. Backend validates the message.

8. Backend stores the reading.

9. Intelligence service processes the reading.

10. Weather information is considered where required.

11. Irrigation/advisory decision is generated.

12. Frontend retrieves and displays the result.

13. SMS service generates/sends the farmer advisory.

14. If irrigation is required, backend publishes an MQTT command.

15. ESP32 receives the command.

16. Virtual pump/relay changes state.

17. ESP32 publishes the new pump status.

18. Backend stores the irrigation event.

19. Frontend displays the updated irrigation state.
```

---

# 27. Definition of "integrated"

The project is considered integrated only when:

```text
[✓] ESP32 produces real simulated sensor readings
[✓] MQTT messages reach HiveMQ
[✓] Backend receives them
[✓] Database stores them
[✓] Intelligence processes them
[✓] Weather can influence the decision
[✓] Frontend displays real backend data
[✓] SMS advisory is generated
[✓] Backend can send an irrigation command
[✓] ESP32 receives the command
[✓] Virtual pump changes state
[✓] Pump status returns through MQTT
[✓] Database records the event
```

---

# 28. Rules for preventing project mismatch

### Rule 1
Do not rename an agreed JSON field without team approval.

### Rule 2
Do not create alternative MQTT topics without documenting them.

### Rule 3
Do not hard-code secrets into source code.

### Rule 4
Do not connect the frontend directly to ESP32 for the main application workflow.

### Rule 5
Do not duplicate the database in multiple backend modules.

### Rule 6
Do not put crop-advisory logic inside the frontend.

### Rule 7
Do not put SMS credentials inside ESP32 firmware.

### Rule 8
Do not assume a sensor unit; document it.

### Rule 9
Every member must test against the current integration contract.

### Rule 10
Any interface change must be communicated to all four members.

---

# 29. Minimum final demonstration

The final demonstration should show:

```text
CIRKIT DESIGNER
      ↓
ESP32
      ↓
Sensor values
      ↓
MQTT
      ↓
HIVEMQ
      ↓
BACKEND
      ↓
DATABASE
      ↓
DECISION ENGINE
      ↓
┌──────────────┬───────────────┐
│              │               │
▼              ▼               ▼
Dashboard     SMS          MQTT Command
                               │
                               ▼
                             ESP32
                               │
                               ▼
                          Virtual Pump
```

This single demonstration proves that the four members' components are not independent projects but one connected SmartFarm system.

---

# 30. Final responsibility summary

| Member | Primary responsibility | Integration output |
|---|---|---|
| Member 1 | ESP32 / Cirkit Designer / sensors / MQTT | Telemetry + pump control |
| Member 2 | MQTT backend / database / REST API | Stored data + APIs |
| Member 3 | Intelligence / weather / irrigation / SMS | Recommendations + commands |
| Member 4 | Frontend | Dashboard using backend APIs |

**Project boundary:**

```text
MEMBER 1
ESP32
  │
  │ MQTT
  ▼
MEMBER 2
MQTT + DATABASE + API
  │
  │ API/data
  ▼
MEMBER 3
INTELLIGENCE + WEATHER + SMS
  │
  ├──────────────► Farmer SMS
  │
  │ API
  ▼
MEMBER 4
FRONTEND
```

**Feedback path:**

```text
MEMBER 3
   │
   │ MQTT command
   ▼
HIVEMQ
   │
   ▼
MEMBER 1
ESP32
   │
   ▼
Virtual Pump
```

---

## Version control

**Version:** 1.0  
**Status:** Initial team integration contract  
**Review required before coding:** Yes  
**Primary rule:** Interfaces must be agreed before implementation.
