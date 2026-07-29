"""Constants for the Meteo Romania (ANM) integration."""

from __future__ import annotations

from datetime import timedelta
import logging

DOMAIN = "meteo_romania"
PLATFORMS = ["sensor", "weather", "binary_sensor"]
LOGGER = logging.getLogger(__package__)

# ========== ANM API ==========
API_BASE_URL = "https://www.meteoromania.ro/wp-json/meteoapi/v2"
API_STAREA_VREMII = f"{API_BASE_URL}/starea-vremii"
API_PROGNOZA_ORASE = f"{API_BASE_URL}/prognoza-orase"
API_AVERTIZARI_GENERALE = f"{API_BASE_URL}/avertizari-generale"
API_AVERTIZARI_NOWCASTING = f"{API_BASE_URL}/avertizari-nowcasting"

# ========== OpenMeteo API (free, no key) ==========
OPENMETEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OPENMETEO_PARAMS_CURRENT = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,"
    "wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
    "surface_pressure,weather_code,cloud_cover,precipitation,is_day"
)
OPENMETEO_PARAMS_DAILY = (
    "weather_code,temperature_2m_max,temperature_2m_min,"
    "precipitation_sum,precipitation_probability_max,"
    "wind_speed_10m_max,wind_gusts_10m_max"
)

# ========== Geocoding (Nominatim - free) ==========
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {"User-Agent": "ha-meteo-romania/1.0"}

# ========== Config entry keys ==========
CONF_CITY = "city"
CONF_FORECAST_CITY = "forecast_city"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_MODE = "mode"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_LOCATION_NAME = "location_name"
CONF_POSTAL_CODE = "postal_code"

# ========== Modes ==========
MODE_ANM_STATION = "anm_station"
MODE_CUSTOM_LOCATION = "custom_location"

# ========== Defaults ==========
DEFAULT_UPDATE_INTERVAL = 1800  # 30 minutes
DEFAULT_FORECAST_CITY = "Bucuresti"

# ========== Update intervals ==========
UPDATE_INTERVAL_STAREA_VREMII = timedelta(minutes=30)
UPDATE_INTERVAL_PROGNOZA = timedelta(hours=3)
UPDATE_INTERVAL_AVERTIZARI = timedelta(minutes=15)
UPDATE_INTERVAL_OPENMETEO = timedelta(minutes=30)

# ========== WMO Weather Codes (OpenMeteo) ==========
# https://open-meteo.com/en/docs
WMO_WEATHER_CODE_MAP = {
    0: "sunny",             # Clear sky
    1: "sunny",             # Mainly clear
    2: "partlycloudy",      # Partly cloudy
    3: "cloudy",            # Overcast
    45: "fog",              # Fog
    48: "fog",              # Depositing rime fog
    51: "rainy",            # Light drizzle
    53: "rainy",            # Moderate drizzle
    55: "rainy",            # Dense drizzle
    56: "rainy",            # Light freezing drizzle
    57: "rainy",            # Dense freezing drizzle
    61: "rainy",            # Slight rain
    63: "rainy",            # Moderate rain
    65: "pouring",          # Heavy rain
    66: "rainy",            # Light freezing rain
    67: "pouring",          # Heavy freezing rain
    71: "snowy",            # Slight snow
    73: "snowy",            # Moderate snow
    75: "snowy",            # Heavy snow
    77: "snowy",            # Snow grains
    80: "rainy",            # Slight rain showers
    81: "rainy",            # Moderate rain showers
    82: "pouring",          # Violent rain showers
    85: "snowy",            # Slight snow showers
    86: "snowy",            # Heavy snow showers
    95: "lightning",        # Thunderstorm
    96: "lightning-rainy",  # Thunderstorm with slight hail
    99: "lightning-rainy",  # Thunderstorm with heavy hail
}

# WMO codes for night (sunny -> clear-night)
WMO_NIGHT_CODE_MAP = {
    0: "clear-night",
    1: "clear-night",
    2: "partlycloudy",
    3: "cloudy",
}

# ========== ANM Icon mapping ==========
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
    "N": 0, "NNE": 22, "NE": 45, "ENE": 67,
    "E": 90, "ESE": 112, "SE": 135, "SSE": 157,
    "S": 180, "SSV": 202, "SV": 225, "VSV": 247,
    "V": 270, "VNV": 292, "NV": 315, "NNV": 337,
}

# Avertizare color codes
AVERTIZARE_COLORS = {
    "0": "galben",
    "1": "portocaliu",
    "2": "roșu",
}

# Forecast city mapping (prognoza-orase only has 10 cities)
FORECAST_CITIES = [
    "Arad", "Botosani", "Bucuresti", "Cluj-Napoca", "Constanta",
    "Craiova", "Iasi", "Rm. Valcea", "Sibiu", "Sulina",
]

# Nearest forecast city fallback mapping
NEAREST_FORECAST_CITY: dict[str, str] = {
    # Argeș region
    "PITESTI": "Bucuresti", "CAMPULUNG MUSCEL": "Bucuresti",
    "CURTEA DE ARGES": "Bucuresti", "TARGOVISTE": "Bucuresti",
    "CAMPINA": "Bucuresti", "PLOIESTI": "Bucuresti",
    "BUCURESTI AFUMATI": "Bucuresti", "BUCURESTI BANEASA": "Bucuresti",
    "BUCURESTI FILARET": "Bucuresti",
    # Oltenia
    "CRAIOVA": "Craiova", "RAMNICU VALCEA": "Rm. Valcea",
    "DRAGASANI": "Rm. Valcea", "SLATINA": "Craiova",
    "CARACAL": "Craiova", "TARGU JIU": "Craiova",
    "DROBETA TURNU SEVERIN": "Craiova", "BAILESTI": "Craiova",
    # Transilvania
    "CLUJ-NAPOCA": "Cluj-Napoca", "SIBIU": "Sibiu",
    "ALBA IULIA": "Sibiu", "BRASOV GHIMBAV": "Sibiu",
    "TARGU MURES": "Cluj-Napoca", "DEVA": "Sibiu",
    "HUNEDOARA": "Sibiu", "SEBES (ALBA)": "Sibiu",
    "BLAJ": "Sibiu", "MIERCUREA CIUC": "Cluj-Napoca",
    "ODORHEIUL SECUIESC": "Cluj-Napoca",
    "SFANTU GHEORGHE (MUNTE)": "Cluj-Napoca",
    # Moldova
    "IASI": "Iasi", "BOTOSANI": "Botosani", "BACAU": "Iasi",
    "GALATI": "Iasi", "BRAILA": "Iasi", "FOCSANI": "Iasi",
    "VASLUI": "Iasi", "SUCEAVA": "Botosani", "PIATRA NEAMT": "Iasi",
    "ROMAN": "Iasi", "ADJUD": "Iasi", "BARLAD": "Iasi",
    "TECUCI": "Iasi", "BUZAU": "Bucuresti", "RAMNICU SARAT": "Bucuresti",
    # Banat
    "ARAD": "Arad", "TIMISOARA": "Arad", "RESITA": "Arad",
    "CARANSEBES": "Arad", "LUGOJ": "Arad",
    # Dobrogea
    "CONSTANTA": "Constanta", "CONSTANTA - dig": "Constanta",
    "MANGALIA": "Constanta", "TULCEA": "Sulina",
    "MEDGIDIA": "Constanta", "SULINA": "Sulina",
    # Maramureș
    "BAIA MARE": "Cluj-Napoca", "SIGHETUL MARMATIEI": "Cluj-Napoca",
    "SATU MARE": "Cluj-Napoca",
    # Bihor
    "ORADEA": "Arad", "BIHOR": "Arad",
    # Bucovina
    "RADAUTI": "Botosani",
}

# Romanian counties for ANM warnings
ROMANIAN_COUNTIES = [
    "AB", "AR", "AG", "BC", "BH", "BN", "BT", "BV", "BR", "B",
    "BZ", "CS", "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR",
    "GJ", "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT",
    "OT", "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VS",
    "VL", "VN",
]

# County code to name mapping
COUNTY_NAMES = {
    "AB": "Alba", "AR": "Arad", "AG": "Argeș", "BC": "Bacău",
    "BH": "Bihor", "BN": "Bistrița-Năsăud", "BT": "Botoșani",
    "BV": "Brașov", "BR": "Brăila", "B": "București",
    "BZ": "Buzău", "CS": "Caraș-Severin", "CL": "Călărași",
    "CJ": "Cluj", "CT": "Constanța", "CV": "Covasna",
    "DB": "Dâmbovița", "DJ": "Dolj", "GL": "Galați",
    "GR": "Giurgiu", "GJ": "Gorj", "HR": "Harghita",
    "HD": "Hunedoara", "IL": "Ialomița", "IS": "Iași",
    "IF": "Ilfov", "MM": "Maramureș", "MH": "Mehedinți",
    "MS": "Mureș", "NT": "Neamț", "OT": "Olt", "PH": "Prahova",
    "SM": "Satu Mare", "SJ": "Sălaj", "SB": "Sibiu",
    "SV": "Suceava", "TR": "Teleorman", "TM": "Timiș",
    "TL": "Tulcea", "VS": "Vaslui", "VL": "Vâlcea",
    "VN": "Vrancea",
}
