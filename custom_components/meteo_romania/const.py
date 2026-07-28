"""Constants for the Meteo Romania (ANM) integration."""

from __future__ import annotations

from datetime import timedelta
import logging

DOMAIN = "meteo_romania"
PLATFORMS = ["sensor", "weather", "binary_sensor"]
LOGGER = logging.getLogger(__package__)

# API
API_BASE_URL = "https://www.meteoromania.ro/wp-json/meteoapi/v2"
API_STAREA_VREMII = f"{API_BASE_URL}/starea-vremii"
API_PROGNOZA_ORASE = f"{API_BASE_URL}/prognoza-orase"
API_AVERTIZARI_GENERALE = f"{API_BASE_URL}/avertizari-generale"
API_AVERTIZARI_NOWCASTING = f"{API_BASE_URL}/avertizari-nowcasting"

# Config entry keys
CONF_CITY = "city"
CONF_FORECAST_CITY = "forecast_city"
CONF_UPDATE_INTERVAL = "update_interval"

# Defaults
DEFAULT_UPDATE_INTERVAL = 1800  # 30 minutes
DEFAULT_FORECAST_CITY = "Bucuresti"

# Update intervals
UPDATE_INTERVAL_STAREA_VREMII = timedelta(minutes=30)
UPDATE_INTERVAL_PROGNOZA = timedelta(hours=3)
UPDATE_INTERVAL_AVERTIZARI = timedelta(minutes=15)

# Icon mapping from ANM icon codes to HA weather conditions
# ANM icons: 2=clear, 3=partly cloudy, 5=overcast, 29=invisible, 84=unavailable
ANM_ICON_MAP = {
    "1": "sunny",
    "2": "sunny",
    "3": "partlycloudy",
    "4": "partlycloudy",
    "5": "cloudy",
    "6": "cloudy",
    "7": "fog",
    "8": "fog",
    "9": "rainy",
    "10": "rainy",
    "11": "rainy",
    "12": "pouring",
    "13": "snowy-rainy",
    "14": "snowy",
    "15": "snowy",
    "16": "snowy",
    "17": "hail",
    "18": "lightning-rainy",
    "19": "lightning",
    "20": "fog",
    "21": "fog",
    "22": "snowy",
    "23": "snowy-rainy",
    "24": "rainy",
    "25": "hail",
    "26": "lightning-rainy",
    "27": "snowy",
    "28": "fog",
    "29": "cloudy",
    "30": "partlycloudy",
    "31": "sunny",
    "32": "windy",
    "33": "clear-night",
    "34": "partlycloudy",
    "35": "cloudy",
    "36": "snowy",
    "37": "fog",
    "38": "rainy",
    "39": "snowy-rainy",
    "40": "rainy",
    "41": "snowy",
    "42": "lightning-rainy",
    "43": "snowy-rainy",
    "44": "snowy",
    "45": "rainy",
    "46": "snowy-rainy",
    "47": "fog",
    "48": "fog",
    "49": "snowy",
    "50": "rainy",
    "51": "snowy-rainy",
    "52": "rainy",
    "53": "snowy",
    "54": "snowy-rainy",
    "55": "hail",
    "56": "hail",
    "57": "snowy",
    "58": "rainy",
    "59": "snowy-rainy",
    "60": "rainy",
    "61": "snowy",
    "62": "snowy-rainy",
    "63": "rainy",
    "64": "snowy",
    "65": "hail",
    "66": "hail",
    "67": "snowy",
    "68": "rainy",
    "69": "snowy-rainy",
    "70": "snowy",
    "71": "snowy",
    "72": "snowy",
    "73": "snowy",
    "74": "snowy",
    "75": "snowy",
    "76": "fog",
    "77": "fog",
    "78": "fog",
    "79": "snowy",
    "80": "rainy",
    "81": "rainy",
    "82": "rainy",
    "83": "snowy-rainy",
    "84": "exceptional",
    "85": "snowy-rainy",
    "86": "snowy-rainy",
    "87": "hail",
    "88": "hail",
    "89": "hail",
    "90": "lightning",
    "91": "lightning-rainy",
    "92": "lightning-rainy",
    "93": "snowy-rainy",
    "94": "snowy-rainy",
    "95": "lightning-rainy",
    "96": "lightning-rainy",
    "97": "lightning-rainy",
    "98": "lightning",
    "99": "lightning",
    "100": "sunny",
    "101": "partlycloudy",
    "102": "cloudy",
    "103": "rainy",
    "104": "snowy",
    "1100": "sunny",
    "1400": "partlycloudy",
    "1460": "rainy",
}

# Forecast symbol mapping (prognoza-orase)
FORECAST_SYMBOL_MAP = {
    "1100": "sunny",
    "1400": "partlycloudy",
    "1460": "rainy",
}

# Nebulozitate (cloudiness) text to HA condition
NEBULOZITATE_MAP = {
    "cer senin": "sunny",
    "cer partial noros": "partlycloudy",
    "cer acoperit": "cloudy",
    "cer invizibil": "fog",
    "indisponibil": "exceptional",
}

# Wind direction mapping
WIND_DIRECTION_MAP = {
    "N": 0,
    "NNE": 22,
    "NE": 45,
    "ENE": 67,
    "E": 90,
    "ESE": 112,
    "SE": 135,
    "SSE": 157,
    "S": 180,
    "SSV": 202,
    "SV": 225,
    "VSV": 247,
    "V": 270,
    "VNV": 292,
    "NV": 315,
    "NNV": 337,
}

# Avertizare color codes
AVERTIZARE_COLORS = {
    "0": "galben",
    "1": "portocaliu",
    "2": "roșu",
}

# Forecast city mapping (prognoza-orase only has 10 cities)
FORECAST_CITIES = [
    "Arad",
    "Botosani",
    "Bucuresti",
    "Cluj-Napoca",
    "Constanta",
    "Craiova",
    "Iasi",
    "Rm. Valcea",
    "Sibiu",
    "Sulina",
]

# Nearest forecast city fallback mapping
# Maps main city names to nearest forecast city
NEAREST_FORECAST_CITY: dict[str, str] = {
    # Argeș region -> București / Rm. Vâlcea
    "PITESTI": "Bucuresti",
    "CAMPULUNG MUSCEL": "Bucuresti",
    "CURTEA DE ARGES": "Bucuresti",
    "TARGOVISTE": "Bucuresti",
    "CAMPINA": "Bucuresti",
    "PLOIESTI": "Bucuresti",
    "BUCURESTI AFUMATI": "Bucuresti",
    "BUCURESTI BANEASA": "Bucuresti",
    "BUCURESTI FILARET": "Bucuresti",
    # Oltenia -> Craiova / Rm. Vâlcea
    "CRAIOVA": "Craiova",
    "RAMNICU VALCEA": "Rm. Valcea",
    "DRAGASANI": "Rm. Valcea",
    "SLATINA": "Craiova",
    "CARACAL": "Craiova",
    "TARGU JIU": "Craiova",
    "DROBETA TURNU SEVERIN": "Craiova",
    "BAILESTI": "Craiova",
    # Transilvania -> Cluj / Sibiu
    "CLUJ-NAPOCA": "Cluj-Napoca",
    "SIBIU": "Sibiu",
    "ALBA IULIA": "Sibiu",
    "BRASOV GHIMBAV": "Sibiu",
    "TARGU MURES": "Cluj-Napoca",
    "DEVA": "Sibiu",
    "HUNEDOARA": "Sibiu",
    "SEBES (ALBA)": "Sibiu",
    "BLAJ": "Sibiu",
    "MIERCUREA CIUC": "Cluj-Napoca",
    "ODORHEIUL SECUIESC": "Cluj-Napoca",
    "SFANTU GHEORGHE (MUNTE)": "Cluj-Napoca",
    # Moldova -> Iași / Botoșani
    "IASI": "Iasi",
    "BOTOSANI": "Botosani",
    "BACAU": "Iasi",
    "GALATI": "Iasi",
    "BRAILA": "Iasi",
    "FOCSANI": "Iasi",
    "VASLUI": "Iasi",
    "SUCEAVA": "Botosani",
    "PIATRA NEAMT": "Iasi",
    "ROMAN": "Iasi",
    "ADJUD": "Iasi",
    "BARLAD": "Iasi",
    "TECUCI": "Iasi",
    "BUZAU": "Bucuresti",
    "RAMNICU SARAT": "Bucuresti",
    # Banat -> Arad / Timișoara
    "ARAD": "Arad",
    "TIMISOARA": "Arad",
    "RESITA": "Arad",
    "CARANSEBES": "Arad",
    "LUGOJ": "Arad",
    # Dobrogea -> Constanța / Sulina
    "CONSTANTA": "Constanta",
    "CONSTANTA - dig": "Constanta",
    "MANGALIA": "Constanta",
    "TULCEA": "Sulina",
    "MEDGIDIA": "Constanta",
    "SULINA": "Sulina",
    # Maramureș -> Cluj
    "BAIA MARE": "Cluj-Napoca",
    "SIGHETUL MARMATIEI": "Cluj-Napoca",
    "SATU MARE": "Cluj-Napoca",
    # Oradea -> Arad
    "ORADEA": "Arad",
    "BIHOR": "Arad",
    # Bucovina -> Botoșani
    "RADAUTI": "Botosani",
    "SUCEAVA": "Botosani",
}
