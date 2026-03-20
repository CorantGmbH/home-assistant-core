"""Diagnostics support for air-Q."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant

from . import AirQConfigEntry
from .const import CONF_CLIP_NEGATIVE, CONF_RETURN_AVERAGE

REDACT_CONFIG = {CONF_PASSWORD, CONF_UNIQUE_ID, CONF_IP_ADDRESS, "title"}
REDACT_DEVICE_INFO = {"identifiers", "name"}
REDACT_COORDINATOR_DATA = {"DeviceID"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AirQConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    return {
        "config_entry": async_redact_data(entry.as_dict(), REDACT_CONFIG),
        "device_info": async_redact_data(
            dict(coordinator.device_info), REDACT_DEVICE_INFO
        ),
        "coordinator_data": async_redact_data(
            coordinator.data, REDACT_COORDINATOR_DATA
        ),
        "options": {
            CONF_CLIP_NEGATIVE: coordinator.clip_negative,
            CONF_RETURN_AVERAGE: coordinator.return_average,
        },
    }
