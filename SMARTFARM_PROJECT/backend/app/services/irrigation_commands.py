"""Irrigation command creation for the agreed MQTT contract."""

from typing import Any, Mapping

from app.intelligence.irrigation_engine import IrrigationDecision


def command_topic(farm_id: str) -> str:
    """Return the command topic for a farm."""

    farm_id = farm_id.strip()
    if not farm_id:
        raise ValueError("farm_id must not be empty")
    return f"smartfarm/{farm_id}/command"


def build_irrigation_command(
    farm_id: str,
    decision: IrrigationDecision,
) -> tuple[str, Mapping[str, Any]] | None:
    """Build an MQTT command only when irrigation is required."""

    if not decision.irrigation_required:
        return None
    if not decision.pump or decision.duration_seconds <= 0:
        raise ValueError("an irrigation command requires an active pump and duration")

    payload = {
        "command": "IRRIGATION",
        "pump": True,
        "duration_seconds": decision.duration_seconds,
        "reason": decision.reason,
    }
    return command_topic(farm_id), payload
