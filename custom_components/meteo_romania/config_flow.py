"""Config flow for Meteo Romania (ANM) integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MeteoRomaniaApiClient
from .const import (
    CONF_CITY,
    CONF_FORECAST_CITY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_FORECAST_CITY,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    FORECAST_CITIES,
    NEAREST_FORECAST_CITY,
)

# All 161 stations sorted alphabetically
ALL_STATIONS = [
    "ADAMCLISI", "ADJUD", "ALBA IULIA", "ALEXANDRIA", "AMZACEA", "ARAD",
    "BACAU", "BACLES", "BAIA MARE", "BAILE HERCULANE", "BAILESTI",
    "BAISOARA", "BALEA LAC", "BANLOC", "BARAOLT", "BARLAD",
    "BARNOVA (RADAR)", "BATOS", "BECHET", "BISOCA", "BISTRITA", "BLAJ",
    "BOITA", "BOROD", "BOTOSANI", "BOZOVICI", "BRAILA", "BRASOV GHIMBAV",
    "BUCIN", "BUCURESTI AFUMATI", "BUCURESTI BANEASA", "BUCURESTI FILARET",
    "BUZAU", "CALAFAT", "CALARASI", "CALIMANI (RETITIS)", "CAMPENI (BISTRA)",
    "CAMPINA", "CAMPULUNG MUSCEL", "CARACAL", "CARANSEBES", "CEAHLAU TOACA",
    "CERNAVODA", "CHISINEU CRIS", "CLUJ-NAPOCA", "CONSTANTA",
    "CONSTANTA - dig", "CORUGEA", "COTNARI", "CRAIOVA", "CUNTU",
    "CURTEA DE ARGES", "DARABANI", "DEDULESTI-MORARESTI", "DEJ", "DEVA",
    "DRAGASANI", "DROBETA TURNU SEVERIN", "DUMBRAVENI",
    "DUMBRAVITA DE CODRU", "FAGARAS", "FETESTI", "FOCSANI", "FUNDATA",
    "GALATI", "GIURGIU", "GORGOVA", "GRIVITA", "GURA PORTITEI", "GURAHONT",
    "HARSOVA", "HOLOD", "HUEDIN", "IASI", "IEZER", "INTORSURA BUZAULUI",
    "JIMBOLIA", "JOSENI", "JURILOVCA", "LACAUTI", "LUGOJ", "MAHMUDIA",
    "MANGALIA", "MEDGIDIA", "MIERCUREA CIUC", "MOLDOVA VECHE",
    "NEGRESTI (VASLUI)", "OCNA SUGATAG", "ODORHEIUL SECUIESC", "OLTENITA",
    "ORADEA", "ORAVITA", "PADES (APA NEAGRA)", "PALTINIS", "PARANG",
    "PATARLAGELE", "PENTELEU", "PETROSANI", "PIATRA NEAMT", "PITESTI",
    "PLOIESTI", "POIANA STAMPEI", "POLOVRAGI", "PREDEAL", "RADAUTI",
    "RAMNICU SARAT", "RAMNICU VALCEA", "RANCA", "RESITA", "ROMAN",
    "ROSIA MONTANA", "ROSIORII DE VEDE", "SACUIENI", "SANNICOLAU MARE",
    "SARMASU", "SATU MARE", "SEBES (ALBA)", "SEMANIC",
    "SFANTU GHEORGHE (DELTA)", "SFANTU GHEORGHE (MUNTE)", "SIBIU",
    "SIGHETUL MARMATIEI", "SINAIA 1500", "SIRIA", "SLATINA", "SLOBOZIA",
    "STANA DE VALE", "STEFANESTI STANCA", "STEI (PETRU GROZA)", "STOLNICI",
    "STRAJA", "SUCEAVA", "SULINA", "SUPURU DE JOS", "TARCU", "TARGOVISTE",
    "TARGU JIU", "TARGU LAPUS", "TARGU LOGRESTI", "TARGU MURES",
    "TARGU NEAMT", "TARGU OCNA", "TARGU SECUIESC", "TARNAVENI (BOBOHALMA)",
    "TEBEA", "TECUCI", "TIMISOARA", "TITU", "TOPLITA", "TULCEA", "TURDA",
    "TURNU MAGURELE", "URZICENI", "VARADIA DE MURES", "VARFUL OMU",
    "VASLUI", "VIDELE", "VLADEASA 1800", "VOINEASA", "ZALAU", "ZIMNICEA",
]


def _get_forecast_city(main_city: str) -> str:
    """Get the nearest forecast city for a given main city."""
    return NEAREST_FORECAST_CITY.get(main_city, DEFAULT_FORECAST_CITY)


async def _validate_station(hass: HomeAssistant, city: str) -> bool:
    """Validate that the station exists in the API."""
    session = async_get_clientsession(hass)
    client = MeteoRomaniaApiClient(session)
    data = await client.get_starea_vremii()
    return city in data


class MeteoRomaniaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteo Romania."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            city = user_input[CONF_CITY]
            forecast_city = _get_forecast_city(city)
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

            # Validate station exists
            if not await _validate_station(self.hass, city):
                errors[CONF_CITY] = "station_not_found"
            else:
                await self.async_set_unique_id(f"{DOMAIN}_{city}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Meteo România - {city.title()}",
                    data={
                        CONF_CITY: city,
                        CONF_FORECAST_CITY: forecast_city,
                        CONF_UPDATE_INTERVAL: update_interval,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CITY): vol.In(ALL_STATIONS),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=DEFAULT_UPDATE_INTERVAL,
                    ): vol.All(vol.Coerce(int), vol.Range(min=300, max=7200)),
                }
            ),
            errors=errors,
        )
