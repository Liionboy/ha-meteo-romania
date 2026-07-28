"""Weather platform for Meteo Romania (ANM)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CITY,
    CONF_FORECAST_CITY,
    DOMAIN,
    NEAREST_FORECAST_CITY,
)
from .coordinator import (
    MeteoRomaniaPrognozaCoordinator,
    MeteoRomaniaStareaVremiiCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo Romania weather from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    starea_coordinator: MeteoRomaniaStareaVremiiCoordinator = data["starea_coordinator"]
    prognoza_coordinator: MeteoRomaniaPrognozaCoordinator = data["prognoza_coordinator"]
    city: str = data["city"]
    forecast_city: str = data["forecast_city"]

    async_add_entities([
        MeteoRomaniaWeather(
            starea_coordinator,
            prognoza_coordinator,
            city,
            forecast_city,
            entry,
        )
    ])


class MeteoRomaniaWeather(
    CoordinatorEntity[MeteoRomaniaStareaVremiiCoordinator],
    WeatherEntity,
):
    """Representation of a Meteo Romania weather entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.MBAR
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    def __init__(
        self,
        starea_coordinator: MeteoRomaniaStareaVremiiCoordinator,
        prognoza_coordinator: MeteoRomaniaPrognozaCoordinator,
        city: str,
        forecast_city: str,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(starea_coordinator)
        self._prognoza_coordinator = prognoza_coordinator
        self._city = city
        self._forecast_city = forecast_city
        self._attr_unique_id = f"{entry.entry_id}_weather"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {city.title()}",
            "manufacturer": "Administrația Națională de Meteorologie",
            "model": "Stație Meteo",
            "entry_type": "service",
        }
        self._attr_translation_key = "meteo_romania"

    def _get_station_data(self):
        """Get current station data."""
        if self.coordinator.data and self._city in self.coordinator.data:
            return self.coordinator.data[self._city]
        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        station = self._get_station_data()
        return station.condition if station else None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        station = self._get_station_data()
        return station.temperature if station else None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        station = self._get_station_data()
        return station.pressure if station else None

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        station = self._get_station_data()
        return station.humidity if station else None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        station = self._get_station_data()
        return station.wind_speed if station else None

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        station = self._get_station_data()
        return station.wind_direction if station else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        station = self._get_station_data()
        attrs: dict[str, Any] = {}
        if station:
            attrs["station"] = station.name
            attrs["updated"] = station.updated
            attrs["cloudiness"] = station.cloudiness
            attrs["pressure_trend"] = station.pressure_trend
        attrs["forecast_city"] = self._forecast_city
        return attrs

    def _build_forecast(self) -> list[Forecast]:
        """Build daily forecast list."""
        if not self._prognoza_coordinator.data:
            return []
        if self._forecast_city not in self._prognoza_coordinator.data:
            return []

        forecast_data = self._prognoza_coordinator.data[self._forecast_city]
        forecasts: list[Forecast] = []

        for day in forecast_data.days:
            try:
                forecast_date = datetime.strptime(day.date, "%Y-%m-%d")
            except (ValueError, TypeError):
                continue

            forecasts.append(Forecast(
                datetime=forecast_date.isoformat(),
                temperature=day.temp_max,
                templow=day.temp_min,
                condition=day.condition,
                precipitation_probability=None,
                precipitation=None,
                wind_speed=None,
                wind_bearing=None,
                humidity=None,
                native_precipitation=None,
            ))

        return forecasts

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        return self._build_forecast()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        return self._build_forecast()
