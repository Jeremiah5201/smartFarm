# Backend

Owners: Members 2 and 3.

Member 2: MQTT ingestion, validation, database and core REST API.
Member 3: intelligence, weather, irrigation decisions and SMS.

## Member 3 starting point

The first independent milestone is the pure intelligence layer in
`app/intelligence/`. It currently contains:

- `irrigation_engine.py` — the configurable irrigation rule from the integration
  specification.
- `crop_advisor.py` — transparent, rule-based advisory generation.
- `weather.py` — provider-independent weather data normalization.
- `app/services/advisory.py` — combines farm readings, weather, and decisions.
- `app/services/irrigation_commands.py` — creates the agreed MQTT command payload.
- `app/services/sms.py` — formats farmer-facing advisory messages.
- `app/services/advisory_notifications.py` — sends actionable advisories by SMS.

These modules do not depend on the database, MQTT, weather provider, or SMS
provider. They can therefore be tested with mocked readings before Member 2's
database interfaces are finalized.

From the `backend` directory, run:

```text
python -m unittest discover -s tests
```

The service modules currently use pure inputs and outputs. Database repositories,
HTTP routes, MQTT publishing, and the SMS provider should be connected after
Member 2 confirms the shared interfaces.

`evaluate_and_send_advisory(...)` sends only `WARNING` and `CRITICAL`
advisories. It returns the evaluation and Africa's Talking delivery result so
Member 2 can persist an `SMSLog` record when the database interface is ready.

The weather adapter uses Open-Meteo for forecast rain probability, temperature,
and humidity. The ESP32 `rain_detected` field remains the current local rain
observation and is combined with the external forecast by the irrigation
engine.

SMS delivery uses Africa's Talking. Keep the username and API key in the local
`.env` file; never commit them. Use the Africa's Talking sandbox and approved
test recipient numbers during testing.

Configuration can be loaded with:

```python
from pathlib import Path

from app.config import load_settings

settings = load_settings(Path(".env"))
sms_client = settings.create_sms_client()
```

Process environment variables override values in `.env`. Missing SMS
credentials raise an explicit configuration error.

To send one controlled Africa's Talking sandbox test SMS containing a generated
sample advisory, first set
`AFRICASTALKING_API_KEY` in the local `.env`, then run:

```text
python scripts/send_test_sms.py <approved-recipient-number>
```

The script prints only the provider status and message ID. Use an approved
sandbox recipient and do not commit the local `.env`.

## Agronomy advisory scope

The crop advisor supports maize, rice, groundnuts, beans, millets, and
soybeans. Its pH and temperature ranges are conservative screening ranges
based on FAO crop-water and Ecocrop guidance plus crop-specific extension
references. They are not universal prescriptions: cultivar, soil texture,
drainage, altitude, local climate, rainfall, and growth stage can change the
recommendation.

Location and growth stage should be supplied before treating an advisory as
site-specific. Production decisions should be confirmed with local extension
advice and soil testing.
