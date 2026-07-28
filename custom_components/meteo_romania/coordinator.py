"""DataUpdateCoordinator for Meteo Romania."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AvertizareData,
    MeteoForecastData,
    MeteoRomaniaApiClient,
    MeteoStationData,
)
from .const import (
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL_AVERTIZARI,
    UPDATE_INTERVAL_PROGNOZA,
)


class MeteoRomaniaStareaVremiiCoordinator(DataUpdateCoordinator[dict[str, MeteoStationData]]):
    """Coordinator for current weather data."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: MeteoRomaniaApiClient,
        update_interval: int,
        entry_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_starea_vremii",
            update_interval=timedelta(seconds=update_interval),
        )
        self.client = client
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, MeteoStationData]:
        """Fetch data from API."""
        try:
            data = await self.client.get_starea_vremii()
        except Exception as err:
            raise UpdateFailed(f"Error fetching starea vremii: {err}") from err
        if not data:
            raise UpdateFailed("No data received from Meteo Romania API")
        return data


class MeteoRomaniaPrognozaCoordinator(DataUpdateCoordinator[dict[str, MeteoForecastData]]):
    """Coordinator for forecast data."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: MeteoRomaniaApiClient,
        entry_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_prognoza",
            update_interval=UPDATE_INTERVAL_PROGNOZA,
        )
        self.client = client
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, MeteoForecastData]:
        """Fetch data from API."""
        try:
            data = await self.client.get_prognoza_orase()
        except Exception as err:
            raise UpdateFailed(f"Error fetching prognoza: {err}") from err
        return data


class MeteoRomaniaAvertizariCoordinator(DataUpdateCoordinator[dict[str, AvertizareData]]):
    """Coordinator for weather warnings."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: MeteoRomaniaApiClient,
        entry_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_avertizari",
            update_interval=UPDATE_INTERVAL_AVERTIZARI,
        )
        self.client = client
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, AvertizareData]:
        """Fetch data from API."""
        try:
            generale = await self.client.get_avertizari_generale()
            nowcasting = await self.client.get_avertizari_nowcasting()
        except Exception as err:
            raise UpdateFailed(f"Error fetching avertizări: {err}") from err
        return {
            "generale": generale,
            "nowcasting": nowcasting,
        }
