"""Sensor platform for Meteo Romania (ANM)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import MeteoStationData, OpenMeteoCurrentData
from .const import (
    CONF_CITY,
    DOMAIN,
    MODE_ANM_STATION,
    MODE_CUSTOM_LOCATION,
    WIND_DIRECTION_MAP,
)
from .coordinator import (
    AnmStareaVremiiCoordinator,
    OpenMeteoCoordinator,
)


# =====================================================================
# ANM Sensor Descriptions
# =====================================================================

@dataclass(frozen=True, kw_only=True)
class AnmSensorEntityDescription(SensorEntityDescription):
    """Describes an ANM sensor entity."""
    value_fn: Callable[[MeteoStationData], float | int | str | None]


ANM_SENSOR_TYPES: tuple[AnmSensorEntityDescription, ...] = (
    AnmSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.temperature,
    ),
    AnmSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.humidity,
    ),
    AnmSensorEntityDescription(
        key="wind_speed",
        translation_key="wind_speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.wind_speed,
    ),
    AnmSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        icon="mdi:weather-windy",
        value_fn=lambda d: d.wind_direction,
    ),
    AnmSensorEntityDescription(
        key="wind_bearing",
        translation_key="wind_bearing",
        native_unit_of_measurement="°",
        icon="mdi:compass-rose",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: WIND_DIRECTION_MAP.get(d.wind_direction) if d.wind_direction else None,
    ),
    AnmSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.pressure,
    ),
    AnmSensorEntityDescription(
        key="pressure_trend",
        translation_key="pressure_trend",
        icon="mdi:gauge",
        value_fn=lambda d: d.pressure_trend,
    ),
    AnmSensorEntityDescription(
        key="cloudiness",
        translation_key="cloudiness",
        icon="mdi:weather-cloudy",
        value_fn=lambda d: d.cloudiness,
    ),
    AnmSensorEntityDescription(
        key="condition",
        translation_key="condition",
        icon="mdi:weather-partly-cloudy",
        value_fn=lambda d: d.condition,
    ),
)


# =====================================================================
# OpenMeteo Sensor Descriptions
# =====================================================================

@dataclass(frozen=True, kw_only=True)
class OpenMeteoSensorEntityDescription(SensorEntityDescription):
    """Describes an OpenMeteo sensor entity."""
    value_fn: Callable[[OpenMeteoCurrentData], float | int | str | None]


OPENMETEO_SENSOR_TYPES: tuple[OpenMeteoSensorEntityDescription, ...] = (
    OpenMeteoSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.temperature,
    ),
    OpenMeteoSensorEntityDescription(
        key="apparent_temperature",
        translation_key="apparent_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.apparent_temperature,
    ),
    OpenMeteoSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.humidity,
    ),
    OpenMeteoSensorEntityDescription(
        key="wind_speed",
        translation_key="wind_speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.wind_speed,
    ),
    OpenMeteoSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        native_unit_of_measurement="°",
        icon="mdi:compass-rose",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.wind_direction,
    ),
    OpenMeteoSensorEntityDescription(
        key="wind_direction_text",
        translation_key="wind_direction_text",
        icon="mdi:weather-windy",
        value_fn=lambda d: d.wind_direction_text,
    ),
    OpenMeteoSensorEntityDescription(
        key="wind_gusts",
        translation_key="wind_gusts",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.wind_gusts,
    ),
    OpenMeteoSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.pressure,
    ),
    OpenMeteoSensorEntityDescription(
        key="cloud_cover",
        translation_key="cloud_cover",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-cloudy",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.cloud_cover,
    ),
    OpenMeteoSensorEntityDescription(
        key="precipitation",
        translation_key="precipitation",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.precipitation,
    ),
    OpenMeteoSensorEntityDescription(
        key="condition",
        translation_key="condition",
        icon="mdi:weather-partly-cloudy",
        value_fn=lambda d: d.condition,
    ),
    OpenMeteoSensorEntityDescription(
        key="weather_code",
        translation_key="weather_code",
        icon="mdi:code-brackets",
        value_fn=lambda d: d.weather_code,
    ),
)


# =====================================================================
# Setup
# =====================================================================

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo Romania sensors from a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    mode = entry_data["mode"]

    entities: list[SensorEntity] = []

    if mode == MODE_ANM_STATION:
        coordinator: AnmStareaVremiiCoordinator = entry_data["starea_coordinator"]
        city: str = entry_data["city"]
        entities = [
            AnmSensor(coordinator, description, city, entry)
            for description in ANM_SENSOR_TYPES
        ]
    else:
        coordinator: OpenMeteoCoordinator = entry_data["openmeteo_coordinator"]
        location_name: str = entry_data["location_name"]
        entities = [
            OpenMeteoSensor(coordinator, description, location_name, entry)
            for description in OPENMETEO_SENSOR_TYPES
        ]

    async_add_entities(entities)


# =====================================================================
# ANM Sensor
# =====================================================================

class AnmSensor(CoordinatorEntity[AnmStareaVremiiCoordinator], SensorEntity):
    """Representation of an ANM sensor."""

    _attr_has_entity_name = True
    entity_description: AnmSensorEntityDescription

    def __init__(
        self,
        coordinator: AnmStareaVremiiCoordinator,
        description: AnmSensorEntityDescription,
        city: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._city = city
        self._attr_unique_id = f"{entry.entry_id}_{city}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {city.title()}",
            "manufacturer": "Administrația Națională de Meteorologie",
            "model": "Stație Meteo ANM",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> float | int | str | None:
        if self.coordinator.data and self._city in self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data[self._city])
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.coordinator.data and self._city in self.coordinator.data:
            station = self.coordinator.data[self._city]
            return {"station": station.name, "updated": station.updated}
        return None


# =====================================================================
# OpenMeteo Sensor
# =====================================================================

class OpenMeteoSensor(CoordinatorEntity[OpenMeteoCoordinator], SensorEntity):
    """Representation of an OpenMeteo sensor."""

    _attr_has_entity_name = True
    entity_description: OpenMeteoSensorEntityDescription

    def __init__(
        self,
        coordinator: OpenMeteoCoordinator,
        description: OpenMeteoSensorEntityDescription,
        location_name: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._location_name = location_name
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {location_name}",
            "manufacturer": "OpenMeteo + ANM",
            "model": "OpenMeteo API",
            "entry_type": "service",
        }

    def _get_current(self) -> OpenMeteoCurrentData | None:
        """Get current weather data."""
        if self.coordinator.data:
            return self.coordinator.data.get("current")
        return None

    @property
    def native_value(self) -> float | int | str | None:
        current = self._get_current()
        if current:
            return self.entity_description.value_fn(current)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        current = self._get_current()
        if current:
            return {
                "location": self._location_name,
                "is_day": current.is_day,
                "time": current.time,
            }
        return None
