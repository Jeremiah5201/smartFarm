import json
import logging
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.api.schemas import TelemetryPayload
from app.config import settings
from app.database.database import SessionLocal
from app.services.ingestion import save_telemetry
from app.mqtt.topics import COMMAND_TOPIC, TELEMETRY_TOPIC

logger = logging.getLogger(__name__)


def process_telemetry_message(db: Session, farm_id: str, raw_payload: bytes | str) -> None:
    """Validate one MQTT message and persist it using the normal ingestion path."""
    try:
        data = json.loads(raw_payload)
        payload = TelemetryPayload.model_validate(data)
        save_telemetry(db, farm_id, payload)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        logger.warning("Rejected telemetry for farm %s: %s", farm_id, error)
        raise


class TelemetrySubscriber:
    def __init__(self, session_factory, broker_settings=settings):
        self.session_factory = session_factory
        self.broker_settings = broker_settings
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            logger.error("MQTT connection failed: %s", reason_code)
            return
        topic = self.broker_settings.mqtt_telemetry_topic or TELEMETRY_TOPIC
        result, _ = client.subscribe(topic, qos=1)
        if result != mqtt.MQTT_ERR_SUCCESS:
            logger.error("MQTT subscription failed for %s with code %s", topic, result)
            return
        logger.info("Subscribed to %s with QoS 1", topic)

    def _on_message(self, client, userdata, message):
        farm_id = message.topic.split("/")[1]
        db = self.session_factory()
        try:
            process_telemetry_message(db, farm_id, message.payload)
        except Exception:
            logger.exception("Failed to process telemetry from %s", message.topic)
        finally:
            db.close()

    def start(self) -> None:
        if not self.broker_settings.mqtt_host:
            raise RuntimeError("MQTT_HOST is required to start the subscriber")
        self.client.username_pw_set(self.broker_settings.mqtt_username, self.broker_settings.mqtt_password)
        if self.broker_settings.mqtt_tls:
            self.client.tls_set()
        self.client.connect(self.broker_settings.mqtt_host, self.broker_settings.mqtt_port)
        self.client.loop_forever()

    def start_background(self) -> None:
        if not self.broker_settings.mqtt_host:
            raise RuntimeError("MQTT_HOST is required to start the subscriber")
        self.client.username_pw_set(self.broker_settings.mqtt_username, self.broker_settings.mqtt_password)
        if self.broker_settings.mqtt_tls:
            self.client.tls_set()
        self.client.connect(self.broker_settings.mqtt_host, self.broker_settings.mqtt_port)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def publish_command(self, farm_id, command_id, command) -> None:
        payload = {
            "command_id": command_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pump": command.pump,
            "duration_sec": command.duration_sec,
            "reason": command.reason,
            "force_override": command.force_override,
        }
        result = self.client.publish(
            COMMAND_TOPIC.format(farm_id=farm_id),
            json.dumps(payload),
            qos=1,
        )
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT command publish failed with code {result.rc}")


if __name__ == "__main__":
    TelemetrySubscriber(SessionLocal).start()