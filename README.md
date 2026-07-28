# Meteo Romania - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/v/release/Liionboy/ha-meteo-romania)](https://github.com/Liionboy/ha-meteo-romania/releases)

Integrare Home Assistant pentru date meteo din România — cu două surse de date:

- **ANM** (Administrația Națională de Meteorologie) — 161 stații meteo + avertizări oficiale
- **OpenMeteo** — date precise pe coordonate GPS pentru orice localitate

## Două moduri de funcționare

### 🏢 Modul 1: Stație ANM
Selectezi una din cele **161 stații meteo** ANM din România. Primești date direct de la stațiile meteo românești + prognoză 5 zile pentru 10 orașe majore.

### 📍 Modul 2: Locație personalizată (OpenMeteo + ANM)
Introdu **codul poștal** sau **numele localității** (ex: `117080` sau `Bălilești`). Integrarea:
1. Caută automat coordonatele GPS (Nominatim/OpenStreetMap)
2. Ia date meteo precise de la **OpenMeteo** (exact pe coordonatele tale)
3. Ia **avertizări oficiale ANM** (cod galben/portocaliu/roșu)
4. Oferă **prognoză 7 zile** cu probabilitate de precipitații

**Ideal pentru localități care nu au stație ANM** (ex: Bălilești, sate, comune).

## Caracteristici

- **Fără API key** — ambele surse sunt gratuite
- **161 stații ANM** + orice locație din România prin GPS
- **Senzori**: temperatură, umiditate, vânt (viteză + direcție + rafale), presiune, nebulozitate, precipitații
- **Weather entity** nativă cu prognoză integrată în dashboard
- **Avertizări meteo** oficiale ANM (cod galben/portocaliu/roșu)
- **Avertizări nowcasting** pentru fenomene imediate
- **Căutare după cod poștal** — introduce `117080` și găsește Bălilești

## Entități create

### Modul ANM Station
| Senzor | Descriere | Unitate |
|--------|-----------|---------|
| `sensor.meteo_romania_temperatura` | Temperatura curentă | °C |
| `sensor.meteo_romania_umiditate` | Umiditatea relativă | % |
| `sensor.meteo_romania_viteza_vant` | Viteza vântului | m/s |
| `sensor.meteo_romania_directie_vant` | Direcția vântului | N/NE/E/SE/S/SV/V/NV |
| `sensor.meteo_romania_presiune` | Presiunea atmosferică | mb |
| `sensor.meteo_romania_cer` | Nebulozitatea | senin/noros/acoperit |

### Modul Custom Location (OpenMeteo)
| Senzor | Descriere | Unitate |
|--------|-----------|---------|
| `sensor.meteo_romania_temperatura` | Temperatura curentă | °C |
| `sensor.meteo_romania_temperatura_percepută` | Temperatura percepută | °C |
| `sensor.meteo_romania_umiditate` | Umiditatea relativă | % |
| `sensor.meteo_romania_viteza_vant` | Viteza vântului | km/h |
| `sensor.meteo_romania_directie_vant` | Direcția vântului | ° |
| `sensor.meteo_romania_rafale` | Rafale vânt | km/h |
| `sensor.meteo_romania_presiune` | Presiunea atmosferică | hPa |
| `sensor.meteo_romania_acoperire_nori` | Acoperire nori | % |
| `sensor.meteo_romania_precipitatii` | Precipitații | mm |
| `sensor.meteo_romania_conditie` | Condiția meteo | sunny/cloudy/rainy/etc. |

### Weather Entity (ambele moduri)
- `weather.meteo_romania` — entitate meteo nativă cu prognoză

### Binary Sensors (ambele moduri)
| Senzor | Descriere |
|--------|-----------|
| `binary_sensor.meteo_romania_avertizare_generale` | Avertizări meteo ANM active |
| `binary_sensor.meteo_romania_avertizari_nowcasting` | Avertizări nowcasting active |

## Instalare

### Prin HACS (Recomandat)

1. Deschide HACS → Integrations
2. Click pe `...` → Custom repositories
3. Adaugă `Liionboy/ha-meteo-romania` ca repository
4. Selectează categoria `Integration`
5. Instalează integrarea
6. Repornește Home Assistant

### Manual

1. Copiază directorul `custom_components/meteo_romania` în directorul `custom_components` al instanței tale HA
2. Repornește Home Assistant

## Configurare

1. Settings → Devices & Services → + Add Integration
2. Caută "Meteo Romania"
3. Alege modul:
   - **Locație personalizată** — introdu cod poștal (ex: `117080`) sau nume localitate
   - **Stație ANM** — selectează din cele 161 stații
4. Confirmă locația și setează intervalul de actualizare

## Exemplu: Bălilești (117080)

1. Adaugă integrarea → "Locație personalizată"
2. Introdu `117080` sau `Bălilești`
3. Selectează "Bălilești (117080) - Argeș"
4. Gata! Primești date meteo precise pentru Bălilești + avertizări ANM

## Date sursă

| Sursă | Date | Actualizare |
|-------|------|-------------|
| [ANM](https://www.meteoromania.ro) | 161 stații, avertizări, prognoză 10 orașe | La fiecare 30 min |
| [OpenMeteo](https://open-meteo.com) | Orice coordonate GPS, prognoză 7 zile | La fiecare 30 min |
| [Nominatim](https://nominatim.openstreetmap.org) | Geocoding (coordonate GPS) | La configurare |

## Suport

- [Raportează o problemă](https://github.com/Liionboy/ha-meteo-romania/issues)
- [Cerere funcționalitate](https://github.com/Liionboy/ha-meteo-romania/issues)

## Licență

MIT License
