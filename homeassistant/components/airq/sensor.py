"""Definition of air-Q sensor platform."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    PRESSURE_HPA,
    SOUND_PRESSURE_WEIGHTED_DBA,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AirQCoordinator
from .const import (
    ACTIVITY_BECQUEREL_PER_CUBIC_METER,
    CONCENTRATION_GRAMS_PER_CUBIC_METER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class AirQEntityDescription(SensorEntityDescription):
    """Describes AirQ sensor entity.

    By default sensor values are exposed as they are.
    """

    value_transform_fn: Callable = lambda x: x


def _index2percent(index_value: float) -> float:
    """Convert index units to percent."""
    return index_value / 10.0


# Keys must match those in the data dictionary
SENSOR_TYPES: list[AirQEntityDescription] = [
    AirQEntityDescription(
        key="nh3_MR100",
        name="Ammonia",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="cl2_M20",
        name="Chlorine",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="co",
        name="CO",
        device_class=SensorDeviceClass.CO,
        native_unit_of_measurement=CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="co2",
        name="CO2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="dewpt",
        name="Dew point",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-thermometer",
    ),
    AirQEntityDescription(
        key="ethanol",
        name="Ethanol",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="ch2o_M10",
        name="Formaldehyde",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="h2s",
        name="H2S",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="health",
        name="Health Index",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heart-pulse",
        value_transform_fn=_index2percent,
    ),
    AirQEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="humidity_abs",
        name="Absolute humidity",
        native_unit_of_measurement=CONCENTRATION_GRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water",
    ),
    AirQEntityDescription(
        key="h2_M1000",
        name="Hydrogen",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="ch4_MIPEX",
        name="Methane",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="n2o",
        name="N2O",
        device_class=SensorDeviceClass.NITROUS_OXIDE,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="no_M250",
        name="NO",
        device_class=SensorDeviceClass.NITROGEN_MONOXIDE,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="no2",
        name="NO2",
        device_class=SensorDeviceClass.NITROGEN_DIOXIDE,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="o3",
        name="Ozone",
        device_class=SensorDeviceClass.OZONE,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="oxygen",
        name="Oxygen",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:leaf",
    ),
    AirQEntityDescription(
        key="performance",
        name="Performance Index",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:head-check",
        value_transform_fn=_index2percent,
    ),
    AirQEntityDescription(
        key="pm1",
        name="PM1",
        device_class=SensorDeviceClass.PM1,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:dots-hexagon",
    ),
    AirQEntityDescription(
        key="pm2_5",
        name="PM2.5",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:dots-hexagon",
    ),
    AirQEntityDescription(
        key="pm10",
        name="PM10",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:dots-hexagon",
    ),
    AirQEntityDescription(
        key="pressure",
        name="Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=PRESSURE_HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="pressure_rel",
        name="Relative pressure",
        native_unit_of_measurement=PRESSURE_HPA,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    AirQEntityDescription(
        key="c3h8_MIPEX",
        name="Propane",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="so2",
        name="SO2",
        device_class=SensorDeviceClass.SULPHUR_DIOXIDE,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="sound",
        name="Noise",
        native_unit_of_measurement=SOUND_PRESSURE_WEIGHTED_DBA,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:ear-hearing",
    ),
    AirQEntityDescription(
        key="sound_max",
        name="Noise (Maximum)",
        native_unit_of_measurement=SOUND_PRESSURE_WEIGHTED_DBA,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:ear-hearing",
    ),
    AirQEntityDescription(
        key="radon",
        name="Radon",
        native_unit_of_measurement=ACTIVITY_BECQUEREL_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radioactive",
    ),
    AirQEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="tvoc",
        name="VOC",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AirQEntityDescription(
        key="tvoc_ionsc",
        name="VOC (Industrial)",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities based on a config entry."""

    coordinator = hass.data[DOMAIN][config.entry_id]
    available_keys = list(coordinator.data.keys())

    # Add sensors under warmup
    status = coordinator.data["Status"]
    if isinstance(status, dict):
        warming_up_sensors = [
            k for k, v in status.items() if "sensor still in warm up phase" in v
        ]
        available_keys.extend(warming_up_sensors)
        _LOGGER.debug(
            "Following %d sensors are warming up: %s",
            len(warming_up_sensors),
            ", ".join(warming_up_sensors),
        )

    # Filter out non-sensor keys
    available_sensors = [
        description for description in SENSOR_TYPES if description.key in available_keys
    ]
    _LOGGER.debug(
        "Identified %d available sensors: %s",
        len(available_sensors),
        ", ".join([sensor.key for sensor in available_sensors]),
    )

    entities = [
        AirQSensor(coordinator, description) for description in available_sensors
    ]
    async_add_entities(entities)


class AirQSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AirQCoordinator,
        description: AirQEntityDescription,
    ) -> None:
        """Initialize a single sensor."""
        super().__init__(coordinator)
        self.entity_description: AirQEntityDescription = description

        self._attr_device_info = coordinator.device_info
        self._attr_name = description.name
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the value reported by the sensor.

        The raw value from the sensor can be additionally transformed
        if value_transform_fn was given in AirQEntityDescription.
        """
        # While a sensor is warming up its key isn't present in the returned dict
        value_raw = self.coordinator.data.get(self.entity_description.key)
        return self.entity_description.value_transform_fn(value_raw)
