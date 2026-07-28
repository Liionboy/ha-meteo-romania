"""The Meteo Romania (ANM) integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AnmApiClient, OpenMeteoApiClient
from .const import (
    CONF_CITY,
    CONF_FORECAST_CITY,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
    MODE_ANM_STATION,
    MODE_CUSTOM_LOCATION,
    PLATFORMS,
)
from .coordinator import (
    AnmAvertizariCoordinator,
    AnmPrognozaCoordinator,
    AnmStareaVremiiCoordinator,
    OpenMeteoCoordinator,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteo Romania from a config entry."""
    session = async_get_clientsession(hass)
    mode = entry.data.get(CONF_MODE, MODE_ANM_STATION)
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    entry_data: dict = {}

    if mode == MODE_ANM_STATION:
        # ========== ANM Station Mode ==========
        city = entry.data[CONF_CITY]
        forecast_city = entry.data.get(CONF_FORECAST_CITY, "Bucuresti")

        anm_client = AnmApiClient(session)

        starea_coordinator = AnmStareaVremiiCoordinator(
            hass, anm_client, update_interval, entry.entry_id
        )
        prognoza_coordinator = AnmPrognozaCoordinator(
            hass, anm_client, entry.entry_id
        )
        avertizari_coordinator = AnmAvertizariCoordinator(
            hass, anm_client, entry.entry_id
        )

        try:
            await starea_coordinator.async_config_entry_first_refresh()
        except Exception as err:
            LOGGER.error("Failed to fetch ANM starea vremii: %s", err)
            return False

        await prognoza_coordinator.async_config_entry_first_refresh()
        await avertizari_coordinator.async_config_entry_first_refresh()

        entry_data = {
            "mode": MODE_ANM_STATION,
            "starea_coordinator": starea_coordinator,
            "prognoza_coordinator": prognoza_coordinator,
            "avertizari_coordinator": avertizari_coordinator,
            "city": city,
            "forecast_city": forecast_city,
        }

    else:
        # ========== Custom Location Mode (OpenMeteo + ANM warnings) ==========
        latitude = entry.data[CONF_LATITUDE]
        longitude = entry.data[CONF_LONGITUDE]
        location_name = entry.data.get(CONF_LOCATION_NAME, "Custom")

        anm_client = AnmApiClient(session)
        openmeteo_client = OpenMeteoApiClient(session)

        openmeteo_coordinator = OpenMeteoCoordinator(
            hass, openmeteo_client, latitude, longitude, entry.entry_id
        )
        avertizari_coordinator = AnmAvertizariCoordinator(
            hass, anm_client, entry.entry_id
        )

        try:
            await openmeteo_coordinator.async_config_entry_first_refresh()
        except Exception as err:
            LOGGER.error("Failed to fetch OpenMeteo data: %s", err)
            return False

        await avertizari_coordinator.async_config_entry_first_refresh()

        entry_data = {
            "mode": MODE_CUSTOM_LOCATION,
            "openmeteo_coordinator": openmeteo_coordinator,
            "avertizari_coordinator": avertizari_coordinator,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
        }

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry_data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries."""
    LOGGER.debug("Migrating from version %s", entry.version)
    return True
