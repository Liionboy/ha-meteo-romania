"""API clients for Meteo Romania (ANM) + OpenMeteo."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import aiohttp

from .const import (
    API_AVERTIZARI_GENERALE,
    API_AVERTIZARI_NOWCASTING,
    API_PROGNOZA_ORASE,
    API_STAREA_VREMII,
    FORECAST_SYMBOL_MAP,
    LOGGER,
    NOMINATIM_BASE_URL,
    NOMINATIM_HEADERS,
    OPENMETEO_BASE_URL,
    OPENMETEO_PARAMS_CURRENT,
    OPENMETEO_PARAMS_DAILY,
    WMO_WEATHER_CODE_MAP,
)


# =====================================================================
# Data classes
# =====================================================================

@dataclass
class MeteoStationData:
    """Data from a single ANM meteo station."""

    name: str
    temperature: float | None
    humidity: int | None
    wind_speed: float | None
    wind_direction: str | None
    pressure: float | None
    pressure_trend: str | None
    cloudiness: str | None
    icon: str | None
    updated: str | None

    @property
    def condition(self) -> str:
        """Return HA weather condition based on icon or cloudiness."""
        from .const import ANM_ICON_MAP, NEBULOZITATE_MAP

        if self.icon and self.icon in ANM_ICON_MAP:
            return ANM_ICON_MAP[self.icon]
        if self.cloudiness and self.cloudiness.lower() in NEBULOZITATE_MAP:
            return NEBULOZITATE_MAP[self.cloudiness.lower()]
        return "exceptional"


@dataclass
class ForecastDay:
    """Single day forecast."""

    date: str
    temp_min: float | None
    temp_max: float | None
    condition: str | None
    description: str | None
    symbol: str | None
    precipitation_sum: float | None = None
    precipitation_probability: int | None = None
    wind_speed_max: float | None = None
    wind_gusts_max: float | None = None


@dataclass
class MeteoForecastData:
    """Forecast data for a city."""

    city: str
    data_date: str | None
    days: list[ForecastDay]


@dataclass
class AvertizareData:
    """Weather warning data."""

    active: bool
    message_type: str | None
    message_type_name: str | None
    color: str | None
    color_name: str | None
    phenomena: str | None
    interval: str | None
    affected_zone: str | None
    message_html: str | None
    message_text: str | None
    issued_at: str | None
    expires_at: str | None
    affected_counties: list[str] | None


@dataclass
class OpenMeteoCurrentData:
    """Current weather from OpenMeteo."""

    temperature: float | None = None
    apparent_temperature: float | None = None
    humidity: int | None = None
    wind_speed: float | None = None
    wind_direction: int | None = None
    wind_gusts: float | None = None
    pressure: float | None = None
    weather_code: int | None = None
    cloud_cover: int | None = None
    precipitation: float | None = None
    condition: str | None = None
    is_day: bool = True
    time: str | None = None

    @property
    def wind_direction_text(self) -> str | None:
        """Convert wind bearing to text direction."""
        if self.wind_direction is None:
            return None
        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSV", "SV", "VSV", "V", "VNV", "NV", "NNV"]
        idx = round(self.wind_direction / 22.5) % 16
        return dirs[idx]


@dataclass
class OpenMeteoForecastData:
    """Forecast data from OpenMeteo."""

    days: list[ForecastDay] = field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None


@dataclass
class GeocodingResult:
    """Geocoding result from Nominatim."""

    name: str
    display_name: str
    latitude: float
    longitude: float
    postal_code: str | None = None
    county: str | None = None
    country: str | None = None


# =====================================================================
# Helper functions
# =====================================================================

def _strip_html(html: str | None) -> str | None:
    """Remove HTML tags from a string."""
    if not html:
        return None
    clean = re.sub(r"<[^>]+>", " ", html)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _parse_pressure(pressure_text: str | None) -> tuple[float | None, str | None]:
    """Parse pressure text like '998.3 mb, in crestere'."""
    if not pressure_text or pressure_text == "indisponibil":
        return None, None
    match = re.match(r"([\d.]+)\s*mb\s*,?\s*(.*)", pressure_text)
    if match:
        return float(match.group(1)), match.group(2).strip() or None
    return None, None


def _parse_wind(wind_text: str | None) -> tuple[float | None, str | None]:
    """Parse wind text like '3.8 m/s, directia : NNV'."""
    if not wind_text or wind_text == "indisponibil":
        return None, None
    match = re.match(r"([\d.]+)\s*m/s\s*,?\s*directia\s*:\s*(.*)", wind_text)
    if match:
        return float(match.group(1)), match.group(2).strip()
    return None, None


def _wmo_to_condition(code: int | None, is_day: bool = True) -> str:
    """Convert WMO weather code to HA condition."""
    if code is None:
        return "exceptional"
    if not is_day and code in (0, 1):
        return "clear-night"
    return WMO_WEATHER_CODE_MAP.get(code, "exceptional")


# =====================================================================
# ANM API Client
# =====================================================================

class AnmApiClient:
    """API client for Meteo Romania (ANM)."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _fetch_json(self, url: str) -> Any:
        """Fetch JSON from URL."""
        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    LOGGER.error("ANM API error %s for %s", resp.status, url)
                    return None
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            LOGGER.error("ANM API request failed: %s", err)
            return None

    async def get_starea_vremii(self) -> dict[str, MeteoStationData]:
        """Fetch current weather for all ANM stations."""
        data = await self._fetch_json(API_STAREA_VREMII)
        if not data or not data.get("success"):
            return {}

        result: dict[str, MeteoStationData] = {}
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            name = props.get("nume", "")
            if not name:
                continue

            pressure, pressure_trend = _parse_pressure(props.get("presiunetext"))
            wind_speed, wind_direction = _parse_wind(props.get("vant"))

            temp_raw = props.get("tempe")
            temperature = None
            if temp_raw and temp_raw != "indisponibil":
                try:
                    temperature = float(temp_raw)
                except (ValueError, TypeError):
                    pass

            humidity_raw = props.get("umezeala")
            humidity = int(humidity_raw) if isinstance(humidity_raw, (int, float)) else None

            result[name] = MeteoStationData(
                name=name,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                pressure=pressure,
                pressure_trend=pressure_trend,
                cloudiness=props.get("nebulozitate"),
                icon=props.get("icon"),
                updated=props.get("actualizat"),
            )

        return result

    async def get_prognoza_orase(self) -> dict[str, MeteoForecastData]:
        """Fetch 5-day forecast for major ANM cities."""
        data = await self._fetch_json(API_PROGNOZA_ORASE)
        if not data or "tara" not in data:
            return {}

        result: dict[str, MeteoForecastData] = {}
        localitati = data["tara"].get("localitate", [])
        if isinstance(localitati, dict):
            localitati = [localitati]

        for loc in localitati:
            attrs = loc.get("@attributes", {})
            city_name = attrs.get("nume", "")
            if not city_name:
                continue

            data_date = loc.get("DataPrognozei")
            prognoze = loc.get("prognoza", [])
            if isinstance(prognoze, dict):
                prognoze = [prognoze]

            days: list[ForecastDay] = []
            for prog in prognoze:
                prog_attrs = prog.get("@attributes", {})
                symbol = prog.get("fenomen_simbol")
                condition = FORECAST_SYMBOL_MAP.get(symbol, "exceptional") if symbol else "exceptional"

                temp_min_raw = prog.get("temp_min")
                temp_max_raw = prog.get("temp_max")
                temp_min = float(temp_min_raw) if temp_min_raw and str(temp_min_raw).replace(".", "").isdigit() else None
                temp_max = float(temp_max_raw) if temp_max_raw and str(temp_max_raw).replace(".", "").isdigit() else None

                days.append(ForecastDay(
                    date=prog_attrs.get("data", ""),
                    temp_min=temp_min,
                    temp_max=temp_max,
                    condition=condition,
                    description=prog.get("fenomen_descriere"),
                    symbol=symbol,
                ))

            result[city_name] = MeteoForecastData(
                city=city_name,
                data_date=data_date,
                days=days,
            )

        return result

    async def get_avertizari_generale(self) -> AvertizareData:
        """Fetch current general weather warnings."""
        data = await self._fetch_json(API_AVERTIZARI_GENERALE)
        return self._parse_avertizare(data)

    async def get_avertizari_nowcasting(self) -> AvertizareData:
        """Fetch current nowcasting warnings."""
        data = await self._fetch_json(API_AVERTIZARI_NOWCASTING)
        if isinstance(data, str):
            return self._empty_avertizare()
        return self._parse_avertizare(data)

    def _parse_avertizare(self, data: Any) -> AvertizareData:
        """Parse avertizare data from API response."""
        if not data:
            return self._empty_avertizare()

        avertizare = data.get("avertizare")
        if not avertizare:
            return self._empty_avertizare()

        attrs = avertizare.get("@attributes", {})
        mesaj_html = attrs.get("mesaj")

        judete_raw = avertizare.get("judet", [])
        if isinstance(judete_raw, dict):
            judete_raw = [judete_raw]
        affected_counties = [
            j.get("@attributes", {}).get("cod", "")
            for j in judete_raw
            if j.get("@attributes", {}).get("cod")
        ]

        return AvertizareData(
            active=True,
            message_type=attrs.get("tipMesaj"),
            message_type_name=attrs.get("numeTipMesaj"),
            color=attrs.get("culoare"),
            color_name=attrs.get("numeCuloare"),
            phenomena=attrs.get("fenomeneVizate"),
            interval=attrs.get("intervalul"),
            affected_zone=attrs.get("zonaAfectata"),
            message_html=mesaj_html,
            message_text=_strip_html(mesaj_html),
            issued_at=attrs.get("dataAparitiei"),
            expires_at=attrs.get("dataExpirarii"),
            affected_counties=affected_counties if affected_counties else None,
        )

    @staticmethod
    def _empty_avertizare() -> AvertizareData:
        """Return empty avertizare data."""
        return AvertizareData(
            active=False, message_type=None, message_type_name=None,
            color=None, color_name=None, phenomena=None, interval=None,
            affected_zone=None, message_html=None, message_text=None,
            issued_at=None, expires_at=None, affected_counties=None,
        )


# =====================================================================
# OpenMeteo API Client (free, no key required)
# =====================================================================

class OpenMeteoApiClient:
    """API client for OpenMeteo (free weather API)."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def get_current_and_forecast(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[OpenMeteoCurrentData | None, OpenMeteoForecastData | None]:
        """Fetch current weather and 7-day forecast for coordinates."""
        params = (
            f"latitude={latitude}&longitude={longitude}"
            f"&current={OPENMETEO_PARAMS_CURRENT}"
            f"&daily={OPENMETEO_PARAMS_DAILY}"
            f"&timezone=auto&forecast_days=7"
        )
        url = f"{OPENMETEO_BASE_URL}?{params}"

        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    LOGGER.error("OpenMeteo API error %s", resp.status)
                    return None, None
                data = await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            LOGGER.error("OpenMeteo API request failed: %s", err)
            return None, None

        # Parse current
        current_raw = data.get("current", {})
        is_day = bool(current_raw.get("is_day", 1))
        weather_code = current_raw.get("weather_code")

        current = OpenMeteoCurrentData(
            temperature=current_raw.get("temperature_2m"),
            apparent_temperature=current_raw.get("apparent_temperature"),
            humidity=int(current_raw["relative_humidity_2m"]) if current_raw.get("relative_humidity_2m") is not None else None,
            wind_speed=current_raw.get("wind_speed_10m"),
            wind_direction=current_raw.get("wind_direction_10m"),
            wind_gusts=current_raw.get("wind_gusts_10m"),
            pressure=current_raw.get("surface_pressure"),
            weather_code=weather_code,
            cloud_cover=current_raw.get("cloud_cover"),
            precipitation=current_raw.get("precipitation"),
            condition=_wmo_to_condition(weather_code, is_day),
            is_day=is_day,
            time=current_raw.get("time"),
        )

        # Parse daily forecast
        daily_raw = data.get("daily", {})
        days: list[ForecastDay] = []
        times = daily_raw.get("time", [])

        for i in range(len(times)):
            code = daily_raw.get("weather_code", [None])[i] if i < len(daily_raw.get("weather_code", [])) else None

            temp_min_raw = daily_raw.get("temperature_2m_min", [None])[i] if i < len(daily_raw.get("temperature_2m_min", [])) else None
            temp_max_raw = daily_raw.get("temperature_2m_max", [None])[i] if i < len(daily_raw.get("temperature_2m_max", [])) else None

            days.append(ForecastDay(
                date=times[i] if i < len(times) else "",
                temp_min=round(temp_min_raw, 1) if temp_min_raw is not None else None,
                temp_max=round(temp_max_raw, 1) if temp_max_raw is not None else None,
                condition=_wmo_to_condition(code),
                description=None,
                symbol=str(code) if code is not None else None,
                precipitation_sum=daily_raw.get("precipitation_sum", [None])[i] if i < len(daily_raw.get("precipitation_sum", [])) else None,
                precipitation_probability=daily_raw.get("precipitation_probability_max", [None])[i] if i < len(daily_raw.get("precipitation_probability_max", [])) else None,
                wind_speed_max=daily_raw.get("wind_speed_10m_max", [None])[i] if i < len(daily_raw.get("wind_speed_10m_max", [])) else None,
                wind_gusts_max=daily_raw.get("wind_gusts_10m_max", [None])[i] if i < len(daily_raw.get("wind_gusts_10m_max", [])) else None,
            ))

        forecast = OpenMeteoForecastData(
            days=days,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            timezone=data.get("timezone"),
        )

        return current, forecast


# =====================================================================
# Geocoding Client (Nominatim - free)
# =====================================================================

class GeocodingClient:
    """Geocoding client using Nominatim (OpenStreetMap)."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def search(
        self,
        query: str,
        country_codes: str = "ro",
        limit: int = 5,
    ) -> list[GeocodingResult]:
        """Search for a location by name or postal code."""
        url = (
            f"{NOMINATIM_BASE_URL}"
            f"?q={query}"
            f"&countrycodes={country_codes}"
            f"&format=json"
            f"&limit={limit}"
            f"&addressdetails=1"
        )

        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
                headers=NOMINATIM_HEADERS,
            ) as resp:
                if resp.status != 200:
                    LOGGER.error("Nominatim API error %s", resp.status)
                    return []
                data = await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            LOGGER.error("Nominatim API request failed: %s", err)
            return []

        results: list[GeocodingResult] = []
        for item in data:
            address = item.get("address", {})
            # Extract county from address
            county = address.get("state", "")
            if "Argeș" in county or "Arges" in county:
                county = "Argeș"
            elif "București" in county or "Bucuresti" in county:
                county = "București"

            results.append(GeocodingResult(
                name=address.get("village") or address.get("town") or address.get("city") or address.get("municipality") or item.get("display_name", "").split(",")[0],
                display_name=item.get("display_name", ""),
                latitude=float(item.get("lat", 0)),
                longitude=float(item.get("lon", 0)),
                postal_code=address.get("postcode"),
                county=county,
                country=address.get("country"),
            ))

        return results

    async def search_postal_code(self, postal_code: str) -> list[GeocodingResult]:
        """Search by Romanian postal code."""
        return await self.search(f"{postal_code} Romania", country_codes="ro")

    async def search_location(self, name: str) -> list[GeocodingResult]:
        """Search by location name in Romania."""
        return await self.search(f"{name} Romania", country_codes="ro")
