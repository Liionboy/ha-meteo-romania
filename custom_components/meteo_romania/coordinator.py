"""DataUpdateCoordinator for Meteo Romania."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AnmApiClient,
    AvertizareData,
    MeteoForecastData,
    MeteoStationData,
    OpenMeteoApiClient,
    OpenMeteoCurrentData,
    OpenMeteoForecastData,
)
from .const import (
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL_AVERTIZARI,
    UPDATE_INTERVAL_OPENMETEO,
    UPDATE_INTERVAL_PROGNOZA,
)


class AnmStareaVremiiCoordinator(DataUpdateCoordinator[dict[str, MeteoStationData]]):
    """Coordinator for ANM current weather data."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: AnmApiClient,
        update_interval: int,
        entry_id: str,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_anm_starea_vremii",
            update_interval=timedelta(seconds=update_interval),
        )
        self.client = client
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, MeteoStationData]:
        try:
            data = await self.client.get_starea_vremii()
        except Exception as err:
            raise UpdateFailed(f"Error fetching ANM starea vremii: {err}") from err
        if not data:
            raise UpdateFailed("No data received from ANM API")
        return data


class AnmPrognozaCoordinator(DataUpdateCoordinator[dict[str, MeteoForecastData]]):
    """Coordinator for ANM forecast data."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: AnmApiClient,
        entry_id: str,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_anm_prognoza",
            update_interval=UPDATE_INTERVAL_PROGNOZA,
        )
        self.client = client
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, MeteoForecastData]:
        try:
            data = await self.client.get_prognoza_orase()
        except Exception as err:
            raise UpdateFailed(f"Error fetching ANM prognoza: {err}") from err
        return data


class AnmAvertizariCoordinator(DataUpdateCoordinator[dict[str, AvertizareData]]):
    """Coordinator for ANM weather warnings."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: AnmApiClient,
        entry_id: str,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_anm_avertizari",
            update_interval=UPDATE_INTERVAL_AVERTIZARI,
        )
        self.client = client
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, AvertizareData]:
        try:
            generale = await self.client.get_avertizari_generale()
            nowcasting = await self.client.get_avertizari_nowcasting()
        except Exception as err:
            raise UpdateFailed(f"Error fetching ANM avertizări: {err}") from err
        return {
            "generale": generale,
            "nowcasting": nowcasting,
        }


class OpenMeteoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for OpenMeteo current + forecast data."""

    config_entry_id: str

    def __init__(
        self,
        hass: HomeAssistant,
        client: OpenMeteoApiClient,
        latitude: float,
        longitude: float,
        entry_id: str,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_openmeteo",
            update_interval=UPDATE_INTERVAL_OPENMETEO,
        )
        self.client = client
        self.latitude = latitude
        self.longitude = longitude
        self.config_entry_id = entry_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            current, forecast = await self.client.get_current_and_forecast(
                self.latitude, self.longitude
            )
        except Exception as err:
            raise UpdateFailed(f"Error fetching OpenMeteo data: {err}") from err
        return {
            "current": current,
            "forecast": forecast,
        }
