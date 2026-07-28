"""The Meteo Romania (ANM) integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MeteoRomaniaApiClient
from .const import (
    CONF_CITY,
    CONF_FORECAST_CITY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
    PLATFORMS,
)
from .coordinator import (
    MeteoRomaniaAvertizariCoordinator,
    MeteoRomaniaPrognozaCoordinator,
    MeteoRomaniaStareaVremiiCoordinator,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteo Romania from a config entry."""
    session = async_get_clientsession(hass)
    client = MeteoRomaniaApiClient(session)

    city = entry.data[CONF_CITY]
    forecast_city = entry.data.get(CONF_FORECAST_CITY, "Bucuresti")
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    # Initialize coordinators
    starea_coordinator = MeteoRomaniaStareaVremiiCoordinator(
        hass, client, update_interval, entry.entry_id
    )
    prognoza_coordinator = MeteoRomaniaPrognozaCoordinator(
        hass, client, entry.entry_id
    )
    avertizari_coordinator = MeteoRomaniaAvertizariCoordinator(
        hass, client, entry.entry_id
    )

    # First refresh
    try:
        await starea_coordinator.async_config_entry_first_refresh()
    except Exception as err:
        LOGGER.error("Failed to fetch starea vremii: %s", err)
        return False

    # Forecast and warnings are optional - don't fail setup if they error
    await prognoza_coordinator.async_config_entry_first_refresh()
    await avertizari_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "starea_coordinator": starea_coordinator,
        "prognoza_coordinator": prognoza_coordinator,
        "avertizari_coordinator": avertizari_coordinator,
        "city": city,
        "forecast_city": forecast_city,
    }

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
