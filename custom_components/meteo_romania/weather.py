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
    MODE_ANM_STATION,
    MODE_CUSTOM_LOCATION,
)
from .coordinator import (
    AnmPrognozaCoordinator,
    AnmStareaVremiiCoordinator,
    OpenMeteoCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo Romania weather from a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    mode = entry_data["mode"]

    if mode == MODE_ANM_STATION:
        async_add_entities([
            AnmWeather(
                entry_data["starea_coordinator"],
                entry_data["prognoza_coordinator"],
                entry_data["city"],
                entry_data["forecast_city"],
                entry,
            )
        ])
    else:
        async_add_entities([
            OpenMeteoWeather(
                entry_data["openmeteo_coordinator"],
                entry_data["location_name"],
                entry,
            )
        ])


# =====================================================================
# ANM Weather Entity
# =====================================================================

class AnmWeather(CoordinatorEntity[AnmStareaVremiiCoordinator], WeatherEntity):
    """Weather entity using ANM data."""

    _attr_name = None
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.MBAR
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    def __init__(
        self,
        starea_coordinator: AnmStareaVremiiCoordinator,
        prognoza_coordinator: AnmPrognozaCoordinator,
        city: str,
        forecast_city: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(starea_coordinator)
        self._prognoza_coordinator = prognoza_coordinator
        self._city = city
        self._forecast_city = forecast_city
        self._attr_unique_id = f"{entry.entry_id}_weather"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {city.title()}",
            "manufacturer": "Administrația Națională de Meteorologie",
            "model": "Stație Meteo ANM",
            "entry_type": "service",
        }

    def _get_station_data(self):
        if self.coordinator.data and self._city in self.coordinator.data:
            return self.coordinator.data[self._city]
        return None

    @property
    def condition(self) -> str | None:
        station = self._get_station_data()
        return station.condition if station else None

    @property
    def native_temperature(self) -> float | None:
        station = self._get_station_data()
        return station.temperature if station else None

    @property
    def native_pressure(self) -> float | None:
        station = self._get_station_data()
        return station.pressure if station else None

    @property
    def humidity(self) -> float | None:
        station = self._get_station_data()
        return station.humidity if station else None

    @property
    def native_wind_speed(self) -> float | None:
        station = self._get_station_data()
        return station.wind_speed if station else None

    @property
    def wind_bearing(self) -> float | str | None:
        station = self._get_station_data()
        return station.wind_direction if station else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        station = self._get_station_data()
        attrs: dict[str, Any] = {}
        if station:
            attrs["station"] = station.name
            attrs["updated"] = station.updated
            attrs["cloudiness"] = station.cloudiness
            attrs["pressure_trend"] = station.pressure_trend
        attrs["forecast_city"] = self._forecast_city
        attrs["data_source"] = "ANM"
        return attrs

    def _build_forecast(self) -> list[Forecast]:
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
            ))
        return forecasts

    @property
    def forecast(self) -> list[Forecast] | None:
        return self._build_forecast()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        return self._build_forecast()


# =====================================================================
# OpenMeteo Weather Entity
# =====================================================================

class OpenMeteoWeather(CoordinatorEntity[OpenMeteoCoordinator], WeatherEntity):
    """Weather entity using OpenMeteo data."""

    _attr_name = None
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR

    def __init__(
        self,
        coordinator: OpenMeteoCoordinator,
        location_name: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._location_name = location_name
        self._attr_unique_id = f"{entry.entry_id}_weather"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Meteo România - {location_name}",
            "manufacturer": "OpenMeteo + ANM",
            "model": "OpenMeteo API",
            "entry_type": "service",
        }

    def _get_current(self):
        if self.coordinator.data:
            return self.coordinator.data.get("current")
        return None

    def _get_forecast_data(self):
        if self.coordinator.data:
            return self.coordinator.data.get("forecast")
        return None

    @property
    def condition(self) -> str | None:
        current = self._get_current()
        return current.condition if current else None

    @property
    def native_temperature(self) -> float | None:
        current = self._get_current()
        return current.temperature if current else None

    @property
    def native_apparent_temperature(self) -> float | None:
        current = self._get_current()
        return current.apparent_temperature if current else None

    @property
    def native_pressure(self) -> float | None:
        current = self._get_current()
        return current.pressure if current else None

    @property
    def humidity(self) -> float | None:
        current = self._get_current()
        return current.humidity if current else None

    @property
    def native_wind_speed(self) -> float | None:
        current = self._get_current()
        return current.wind_speed if current else None

    @property
    def wind_bearing(self) -> float | str | None:
        current = self._get_current()
        return current.wind_direction if current else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        current = self._get_current()
        attrs: dict[str, Any] = {
            "location": self._location_name,
            "data_source": "OpenMeteo",
        }
        if current:
            attrs["is_day"] = current.is_day
            attrs["cloud_cover"] = current.cloud_cover
            attrs["wind_gusts"] = current.wind_gusts
            attrs["precipitation"] = current.precipitation
            attrs["rain"] = current.rain
            attrs["snowfall"] = current.snowfall
            attrs["snow_depth"] = current.snow_depth
            attrs["weather_code"] = current.weather_code
            attrs["uv_index"] = current.uv_index
            attrs["visibility"] = current.visibility
            attrs["sunshine_duration"] = current.sunshine_duration
            attrs["shortwave_radiation"] = current.shortwave_radiation
            attrs["soil_temperature"] = current.soil_temperature_0_to_7cm
            attrs["soil_moisture"] = current.soil_moisture_0_to_7cm
        return attrs

    def _build_forecast(self) -> list[Forecast]:
        forecast_data = self._get_forecast_data()
        if not forecast_data:
            return []

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
                precipitation_probability=day.precipitation_probability,
                native_precipitation=day.precipitation_sum,
                wind_speed=day.wind_speed_max,
            ))
        return forecasts

    @property
    def forecast(self) -> list[Forecast] | None:
        return self._build_forecast()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        return self._build_forecast()
