"""Binary sensor platform for Meteo Romania (ANM)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AvertizareData
from .const import CONF_CITY, DOMAIN, MODE_ANM_STATION
from .coordinator import AnmAvertizariCoordinator

_DEFAULT_AVERTIZARE = AvertizareData(
    active=False, message_type=None, message_type_name=None,
    color=None, color_name=None, phenomena=None, interval=None,
    affected_zone=None, message_html=None, message_text=None,
    issued_at=None, expires_at=None, affected_counties=None,
)


@dataclass(frozen=True, kw_only=True)
class MeteoRomaniaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Meteo Romania binary sensor entity."""

    value_fn: Callable[[dict[str, AvertizareData]], bool]
    attrs_fn: Callable[[dict[str, AvertizareData]], dict[str, Any]] | None = None


BINARY_SENSOR_TYPES: tuple[MeteoRomaniaBinarySensorEntityDescription, ...] = (
    MeteoRomaniaBinarySensorEntityDescription(
        key="avertizare_generale",
        name="Avertizare Meteo",
        icon="mdi:alert-circle",
        device_class=BinarySensorDeviceClass.SAFETY,
        value_fn=lambda data: data.get("generale", _DEFAULT_AVERTIZARE).active,
        attrs_fn=lambda data: _build_avertizare_attrs(data.get("generale")),
    ),
    MeteoRomaniaBinarySensorEntityDescription(
        key="avertizari_nowcasting",
        name="Avertizare Nowcasting",
        icon="mdi:alert-circle",
        device_class=BinarySensorDeviceClass.SAFETY,
        value_fn=lambda data: data.get("nowcasting", _DEFAULT_AVERTIZARE).active,
        attrs_fn=lambda data: _build_avertizare_attrs(data.get("nowcasting")),
    ),
)


def _build_avertizare_attrs(avertizare: AvertizareData | None) -> dict[str, Any]:
    """Build attributes dict from AvertizareData."""
    if not avertizare or not avertizare.active:
        return {}
    attrs: dict[str, Any] = {}
    if avertizare.message_type_name:
        attrs["tip_mesaj"] = avertizare.message_type_name
    if avertizare.color_name:
        attrs["cod_culoare"] = avertizare.color_name
    if avertizare.phenomena:
        attrs["fenomene_vizate"] = avertizare.phenomena
    if avertizare.interval:
        attrs["interval"] = avertizare.interval
    if avertizare.affected_zone:
        attrs["zona_afectata"] = avertizare.affected_zone
    if avertizare.message_text:
        attrs["mesaj"] = avertizare.message_text
    if avertizare.issued_at:
        attrs["data_aparitiei"] = avertizare.issued_at
    if avertizare.expires_at:
        attrs["data_expirarii"] = avertizare.expires_at
    if avertizare.affected_counties:
        attrs["judete_afectate"] = ", ".join(avertizare.affected_counties)
    return attrs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo Romania binary sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: AnmAvertizariCoordinator = data["avertizari_coordinator"]

    mode = data.get("mode", MODE_ANM_STATION)
    if mode == MODE_ANM_STATION:
        location = data.get("city", "Romania")
    else:
        location = data.get("location_name", "Romania")

    entities = [
        MeteoRomaniaBinarySensor(coordinator, description, location, entry)
        for description in BINARY_SENSOR_TYPES
    ]
    async_add_entities(entities)


class MeteoRomaniaBinarySensor(
    CoordinatorEntity[AnmAvertizariCoordinator],
    BinarySensorEntity,
):
    """Representation of a Meteo Romania binary sensor."""

    entity_description: MeteoRomaniaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AnmAvertizariCoordinator,
        description: MeteoRomaniaBinarySensorEntityDescription,
        location: str,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._location = location
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {location.title()}",
            "manufacturer": "Administrația Națională de Meteorologie",
            "model": "Stație Meteo",
            "entry_type": "service",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.coordinator.data and self.entity_description.attrs_fn:
            return self.entity_description.attrs_fn(self.coordinator.data)
        return None
