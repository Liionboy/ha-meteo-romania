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

from .api import MeteoStationData
from .const import CONF_CITY, DOMAIN, WIND_DIRECTION_MAP
from .coordinator import MeteoRomaniaStareaVremiiCoordinator


@dataclass(frozen=True, kw_only=True)
class MeteoRomaniaSensorEntityDescription(SensorEntityDescription):
    """Describes a Meteo Romania sensor entity."""

    value_fn: Callable[[MeteoStationData], float | int | str | None]


SENSOR_TYPES: tuple[MeteoRomaniaSensorEntityDescription, ...] = (
    MeteoRomaniaSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.temperature,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.humidity,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="wind_speed",
        translation_key="wind_speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.wind_speed,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        icon="mdi:weather-windy",
        value_fn=lambda data: data.wind_direction,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="wind_bearing",
        translation_key="wind_bearing",
        native_unit_of_measurement="°",
        icon="mdi:compass-rose",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (
            WIND_DIRECTION_MAP.get(data.wind_direction)
            if data.wind_direction
            else None
        ),
    ),
    MeteoRomaniaSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        native_unit_of_measurement=UnitOfPressure.MBAR,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.pressure,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="pressure_trend",
        translation_key="pressure_trend",
        icon="mdi:gauge",
        value_fn=lambda data: data.pressure_trend,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="cloudiness",
        translation_key="cloudiness",
        icon="mdi:weather-cloudy",
        value_fn=lambda data: data.cloudiness,
    ),
    MeteoRomaniaSensorEntityDescription(
        key="condition",
        translation_key="condition",
        icon="mdi:weather-partly-cloudy",
        value_fn=lambda data: data.condition,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo Romania sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: MeteoRomaniaStareaVremiiCoordinator = data["starea_coordinator"]
    city: str = data["city"]

    entities = [
        MeteoRomaniaSensor(coordinator, description, city, entry)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class MeteoRomaniaSensor(CoordinatorEntity[MeteoRomaniaStareaVremiiCoordinator], SensorEntity):
    """Representation of a Meteo Romania sensor."""

    _attr_has_entity_name = True
    entity_description: MeteoRomaniaSensorEntityDescription

    def __init__(
        self,
        coordinator: MeteoRomaniaStareaVremiiCoordinator,
        description: MeteoRomaniaSensorEntityDescription,
        city: str,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._city = city
        self._attr_unique_id = f"{entry.entry_id}_{city}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {city.title()}",
            "manufacturer": "Administrația Națională de Meteorologie",
            "model": "Stație Meteo",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        if self.coordinator.data and self._city in self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data[self._city])
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.coordinator.data and self._city in self.coordinator.data:
            station = self.coordinator.data[self._city]
            return {
                "station": station.name,
                "updated": station.updated,
            }
        return None
