# Meteo Romania (ANM) - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/v/release/Liionboy/ha-meteo-romania)](https://github.com/Liionboy/ha-meteo-romania/releases)

Integrare Home Assistant pentru datele meteo oferite de **Administrația Națională de Meteorologie (ANM)** din România.

## Caracteristici

- **161 stații meteo** din toată România (temperatură, umiditate, vânt, presiune, nebulozitate)
- **Prognoză 5 zile** pentru 10 orașe majore (București, Cluj, Iași, Timișoara, etc.)
- **Avertizări meteo** în timp real (cod galben/portocaliu/roșu)
- **Avertizări nowcasting** pentru fenomene imediate
- **Weather entity** nativă cu prognoză integrată în dashboard
- **Fără API key** — date gratuite de la ANM

## Entități create

### Senzori (per stație)
| Senzor | Descriere | Unitate |
|--------|-----------|---------|
| `sensor.meteo_romania_temperatura` | Temperatura curentă | °C |
| `sensor.meteo_romania_umiditate` | Umiditatea relativă | % |
| `sensor.meteo_romania_viteza_vant` | Viteza vântului | m/s |
| `sensor.meteo_romania_directie_vant` | Direcția vântului | N/NE/E/SE/S/SV/V/NV |
| `sensor.meteo_romania_presiune` | Presiunea atmosferică | mb |
| `sensor.meteo_romania_presiune_trend` | Tendința presiunii | în creștere/scădere |
| `sensor.meteo_romania_cer` | Nebulozitatea | senin/noros/acoperit |
| `sensor.meteo_romania_condiție` | Condiția meteo | sunny/cloudy/rainy/etc. |

### Weather Entity
- `weather.meteo_romania` — entitate meteo nativă cu prognoză 5 zile
- Afișează temperatura, umiditatea, vântul și presiunea curentă
- Prognoza se actualizează la fiecare 3 ore

### Binary Sensors (Avertizări)
| Senzor | Descriere |
|--------|-----------|
| `binary_sensor.meteo_romania_avertizare_generale` | Avertizări meteo active (cod galben/portocaliu/roșu) |
| `binary_sensor.meteo_romania_avertizari_nowcasting` | Avertizări nowcasting active |

**Atribute avertizări:**
- `tip_mesaj` — Tipul avertizării (Atenționare/Alertă)
- `cod_culoare` — Codul de culoare (galben/portocaliu/roșu)
- `fenomene_vizate` — Fenomenele vizate
- `interval` — Intervalul de valabilitate
- `zona_afectata` — Zona afectată
- `mesaj` — Mesajul complet
- `judete_afectate` — Județele afectate

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
2. Caută "Meteo Romania (ANM)"
3. Selectează orașul/stația meteo din dropdown (161 opțiuni)
4. Setează intervalul de actualizare (implicit: 30 minute)

## Date sursă

Toate datele sunt furnizate de [Administrația Națională de Meteorologie](https://www.meteoromania.ro) prin API-ul public:

- **Starea vremii** — actualizat la fiecare oră
- **Prognoza** — actualizat zilnic
- **Avertizările** — actualizat la fiecare 15 minute

## Prognoză

Prognoza pe 5 zile este disponibilă doar pentru 10 orașe majore:
Arad, Botoșani, **București**, Cluj-Napoca, Constanța, Craiova, Iași, Rm. Vâlcea, Sibiu, Sulina

Pentru celelalte orașe, integrarea va folosi automat cel mai apropiat oraș cu prognoză.

## Suport

- [Raportează o problemă](https://github.com/Liionboy/ha-meteo-romania/issues)
- [Cerere funcționalitate](https://github.com/Liionboy/ha-meteo-romania/issues)

## Licență

MIT License
