"""Diagnostics support for Meteo Romania."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, MODE_ANM_STATION


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a Meteo Romania config entry."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    mode = data.get("mode")

    diagnostics: dict[str, Any] = {
        "entry": {
            "mode": mode,
            "title": entry.title,
            "update_interval": entry.data.get("update_interval"),
        },
        "coordinators": {},
    }

    # Coordinator health — the key info when an API changes format
    for key, value in data.items():
        if key.endswith("_coordinator"):
            diagnostics["coordinators"][key] = {
                "last_update_success": bool(value.last_update_success),
                "update_interval": str(value.update_interval),
            }

    if mode == MODE_ANM_STATION:
        starea = data.get("starea_coordinator")
        stations = starea.data if starea else {}
        prognoza = data.get("prognoza_coordinator")
        forecast = prognoza.data if prognoza else {}
        avertizari = data.get("avertizari_coordinator")

        diagnostics["anm"] = {
            "city": data.get("city"),
            "forecast_city": data.get("forecast_city"),
            "stations_received": len(stations) if isinstance(stations, dict) else 0,
            "forecast_cities_received": (
                len(forecast) if isinstance(forecast, dict) else 0
            ),
            "avertizari_generale_active": bool(
                avertizari.data.get("generale", {}).get("active")
            )
            if avertizari and isinstance(avertizari.data, dict)
            else None,
            "nowcasting_active": bool(
                avertizari.data.get("nowcasting", {}).get("active")
            )
            if avertizari and isinstance(avertizari.data, dict)
            else None,
        }
    else:
        openmeteo = data.get("openmeteo_coordinator")
        current = openmeteo.data.get("current") if openmeteo else None
        diagnostics["location"] = {
            "name": data.get("location_name"),
            # Rounded to ~1 km precision: enough to debug OpenMeteo calls
            # without exposing exact home coordinates in shared diagnostics.
            "latitude": round(data["latitude"], 2),
            "longitude": round(data["longitude"], 2),
            "last_update_success": (
                bool(openmeteo.last_update_success) if openmeteo else None
            ),
            "has_current_data": current is not None,
        }

    return diagnostics
