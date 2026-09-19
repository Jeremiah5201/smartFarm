# Database Schema

The first Member 2 migration creates these core tables:

## farmers

`farmer_id`, `name`, `phone_number`, `location`, `preferred_language`.

## farms

`farm_id`, `farmer_id`, `farm_name`, `location`, `crop`, `device_id`.
`farm_id` is the MQTT path identifier, for example `FARM001`.

## sensor_readings

`id`, `farm_id`, `device_id`, `timestamp`, `soil_moisture`, `soil_ph`,
`temperature`, `humidity`, `light`, `rain_detected`, `water_level`, and
`pump_status`.

`farm_id` references `farms.farm_id`; readings are ordered newest first by
`timestamp` through the REST API.

Irrigation events, advisories, and SMS logs belong to Member 3's intelligence
deliverables and can reference `farms` or `farmers` when that work is added.
