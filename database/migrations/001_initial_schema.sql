-- SQLite reference migration for the Member 2 core schema.
-- Application bootstrap uses SQLAlchemy metadata; this is the equivalent
-- explicit migration for environments that manage schema changes separately.

CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INTEGER PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    location VARCHAR(200),
    preferred_language VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS farms (
    farm_id VARCHAR(50) PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(farmer_id),
    farm_name VARCHAR(120) NOT NULL,
    location VARCHAR(200),
    crop VARCHAR(100),
    device_id VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY,
    farm_id VARCHAR(50) NOT NULL REFERENCES farms(farm_id),
    device_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    soil_moisture FLOAT NOT NULL,
    soil_ph FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    light FLOAT NOT NULL,
    rain_detected BOOLEAN NOT NULL,
    water_level FLOAT NOT NULL,
    pump_status BOOLEAN NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_sensor_readings_farm_timestamp
    ON sensor_readings (farm_id, timestamp);

CREATE TABLE IF NOT EXISTS irrigation_events (
    id INTEGER PRIMARY KEY,
    farm_id VARCHAR(50) NOT NULL REFERENCES farms(farm_id),
    timestamp DATETIME NOT NULL,
    duration_seconds INTEGER NOT NULL,
    reason VARCHAR(500) NOT NULL,
    pump_status BOOLEAN NOT NULL,
    command_id VARCHAR(80) UNIQUE
);