"""Config flow for Meteo Romania (ANM) integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AnmApiClient, GeocodingClient
from .const import (
    CONF_CITY,
    CONF_FORECAST_CITY,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_POSTAL_CODE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_FORECAST_CITY,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MODE_ANM_STATION,
    MODE_CUSTOM_LOCATION,
    NEAREST_FORECAST_CITY,
)

# All 161 ANM stations sorted alphabetically
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
    """Get the nearest forecast city for a given ANM station."""
    return NEAREST_FORECAST_CITY.get(main_city, DEFAULT_FORECAST_CITY)


async def _validate_anm_station(hass: HomeAssistant, city: str) -> bool:
    """Validate that the ANM station exists."""
    session = async_get_clientsession(hass)
    client = AnmApiClient(session)
    data = await client.get_starea_vremii()
    return city in data


async def _search_location(
    hass: HomeAssistant, query: str
) -> list[dict[str, Any]]:
    """Search for a location by name or postal code."""
    session = async_get_clientsession(hass)
    client = GeocodingClient(session)

    # Try postal code first if it looks like one
    if query.strip().isdigit() and len(query.strip()) == 6:
        results = await client.search_postal_code(query.strip())
    else:
        results = await client.search_location(query.strip())

    return [
        {
            "name": r.name,
            "display_name": r.display_name,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "postal_code": r.postal_code,
            "county": r.county,
        }
        for r in results
    ]


class MeteoRomaniaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteo Romania."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._mode: str | None = None
        self._location_results: list[dict[str, Any]] = []
        self._selected_location: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - choose mode."""
        if user_input is not None:
            self._mode = user_input[CONF_MODE]
            if self._mode == MODE_ANM_STATION:
                return await self.async_step_anm_station()
            return await self.async_step_custom_location()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODE, default=MODE_CUSTOM_LOCATION): vol.In(
                        {
                            MODE_CUSTOM_LOCATION: "Locație personalizată (cod poștal / oraș)",
                            MODE_ANM_STATION: "Stație ANM (161 stații din România)",
                        }
                    ),
                }
            ),
        )

    async def async_step_anm_station(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle ANM station selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            city = user_input[CONF_CITY]
            forecast_city = _get_forecast_city(city)
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

            if not await _validate_anm_station(self.hass, city):
                errors[CONF_CITY] = "station_not_found"
            else:
                await self.async_set_unique_id(f"{DOMAIN}_anm_{city}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Meteo România - {city.title()}",
                    data={
                        CONF_MODE: MODE_ANM_STATION,
                        CONF_CITY: city,
                        CONF_FORECAST_CITY: forecast_city,
                        CONF_UPDATE_INTERVAL: update_interval,
                    },
                )

        return self.async_show_form(
            step_id="anm_station",
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

    async def async_step_custom_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle custom location search."""
        errors: dict[str, str] = {}

        if user_input is not None:
            query = user_input.get(CONF_POSTAL_CODE, "").strip()
            if not query:
                errors["base"] = "no_query"
            else:
                self._location_results = await _search_location(self.hass, query)
                if not self._location_results:
                    errors["base"] = "location_not_found"
                else:
                    return await self.async_step_select_location()

        return self.async_show_form(
            step_id="custom_location",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POSTAL_CODE): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle location selection from search results."""
        if user_input is not None:
            idx = int(user_input["location"])
            self._selected_location = self._location_results[idx]
            return await self.async_step_confirm_location()

        # Build options from results
        options = {}
        for i, loc in enumerate(self._location_results):
            label = loc["name"]
            if loc.get("postal_code"):
                label += f" ({loc['postal_code']})"
            if loc.get("county"):
                label += f" - {loc['county']}"
            options[str(i)] = label

        return self.async_show_form(
            step_id="select_location",
            data_schema=vol.Schema(
                {
                    vol.Required("location"): vol.In(options),
                }
            ),
        )

    async def async_step_confirm_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm location and set update interval."""
        if user_input is not None:
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            loc = self._selected_location
            name = loc["name"]

            await self.async_set_unique_id(
                f"{DOMAIN}_custom_{loc['latitude']:.4f}_{loc['longitude']:.4f}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Meteo România - {name}",
                data={
                    CONF_MODE: MODE_CUSTOM_LOCATION,
                    CONF_LOCATION_NAME: name,
                    CONF_LATITUDE: loc["latitude"],
                    CONF_LONGITUDE: loc["longitude"],
                    CONF_POSTAL_CODE: loc.get("postal_code"),
                    CONF_UPDATE_INTERVAL: update_interval,
                },
            )

        loc = self._selected_location
        desc = f"📍 {loc['name']}"
        if loc.get("county"):
            desc += f", {loc['county']}"
        desc += f"\n🌐 {loc['latitude']:.4f}, {loc['longitude']:.4f}"

        return self.async_show_form(
            step_id="confirm_location",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=DEFAULT_UPDATE_INTERVAL,
                    ): vol.All(vol.Coerce(int), vol.Range(min=300, max=7200)),
                }
            ),
            description_placeholders={"location_info": desc},
        )
