"""API client for Meteo Romania (ANM)."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any

import aiohttp

from .const import (
    API_AVERTIZARI_GENERALE,
    API_AVERTIZARI_NOWCASTING,
    API_PROGNOZA_ORASE,
    API_STAREA_VREMII,
    LOGGER,
)


@dataclass
class MeteoStationData:
    """Data from a single meteo station."""

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
    temp_min: int | None
    temp_max: int | None
    condition: str | None
    description: str | None
    symbol: str | None


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


def _strip_html(html: str | None) -> str | None:
    """Remove HTML tags from a string."""
    if not html:
        return None
    clean = re.sub(r"<[^>]+>", " ", html)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _parse_pressure(pressure_text: str | None) -> tuple[float | None, str | None]:
    """Parse pressure text like '998.3 mb, in crestere' into (value, trend)."""
    if not pressure_text or pressure_text == "indisponibil":
        return None, None
    match = re.match(r"([\d.]+)\s*mb\s*,?\s*(.*)", pressure_text)
    if match:
        value = float(match.group(1))
        trend = match.group(2).strip() if match.group(2) else None
        return value, trend
    return None, None


def _parse_wind(wind_text: str | None) -> tuple[float | None, str | None]:
    """Parse wind text like '3.8 m/s, directia : NNV' into (speed, direction)."""
    if not wind_text or wind_text == "indisponibil":
        return None, None
    match = re.match(r"([\d.]+)\s*m/s\s*,?\s*directia\s*:\s*(.*)", wind_text)
    if match:
        speed = float(match.group(1))
        direction = match.group(2).strip()
        return speed, direction
    return None, None


class MeteoRomaniaApiClient:
    """API client for Meteo Romania."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def _fetch_json(self, url: str) -> Any:
        """Fetch JSON from URL."""
        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    LOGGER.error("Meteo Romania API error %s for %s", resp.status, url)
                    return None
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            LOGGER.error("Meteo Romania API request failed: %s", err)
            return None

    async def get_starea_vremii(self) -> dict[str, MeteoStationData]:
        """Fetch current weather for all stations."""
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
            humidity = None
            if isinstance(humidity_raw, (int, float)):
                humidity = int(humidity_raw)

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
        """Fetch 5-day forecast for major cities."""
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

                from .const import FORECAST_SYMBOL_MAP

                condition = FORECAST_SYMBOL_MAP.get(symbol, "exceptional") if symbol else "exceptional"

                temp_min_raw = prog.get("temp_min")
                temp_max_raw = prog.get("temp_max")
                temp_min = int(temp_min_raw) if temp_min_raw and temp_min_raw.isdigit() else None
                temp_max = int(temp_max_raw) if temp_max_raw and temp_max_raw.isdigit() else None

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
        if not data:
            return AvertizareData(
                active=False, message_type=None, message_type_name=None,
                color=None, color_name=None, phenomena=None, interval=None,
                affected_zone=None, message_html=None, message_text=None,
                issued_at=None, expires_at=None, affected_counties=None,
            )

        avertizare = data.get("avertizare")
        if not avertizare:
            return AvertizareData(
                active=False, message_type=None, message_type_name=None,
                color=None, color_name=None, phenomena=None, interval=None,
                affected_zone=None, message_html=None, message_text=None,
                issued_at=None, expires_at=None, affected_counties=None,
            )

        attrs = avertizare.get("@attributes", {})
        mesaj_html = attrs.get("mesaj")
        mesaj_text = _strip_html(mesaj_html)

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
            message_text=mesaj_text,
            issued_at=attrs.get("dataAparitiei"),
            expires_at=attrs.get("dataExpirarii"),
            affected_counties=affected_counties if affected_counties else None,
        )

    async def get_avertizari_nowcasting(self) -> AvertizareData:
        """Fetch current nowcasting warnings."""
        data = await self._fetch_json(API_AVERTIZARI_NOWCASTING)
        if not data or isinstance(data, str):
            return AvertizareData(
                active=False, message_type=None, message_type_name=None,
                color=None, color_name=None, phenomena=None, interval=None,
                affected_zone=None, message_html=None, message_text=None,
                issued_at=None, expires_at=None, affected_counties=None,
            )

        avertizare = data.get("avertizare")
        if not avertizare:
            return AvertizareData(
                active=False, message_type=None, message_type_name=None,
                color=None, color_name=None, phenomena=None, interval=None,
                affected_zone=None, message_html=None, message_text=None,
                issued_at=None, expires_at=None, affected_counties=None,
            )

        attrs = avertizare.get("@attributes", {})
        mesaj_html = attrs.get("mesaj")
        mesaj_text = _strip_html(mesaj_html)

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
            message_text=mesaj_text,
            issued_at=attrs.get("dataAparitiei"),
            expires_at=attrs.get("dataExpirarii"),
            affected_counties=affected_counties if affected_counties else None,
        )
