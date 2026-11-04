# Clear-Sky Solar Integration for Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/docs/faq/custom_repositories/)

Clear-Sky Solar provides calculated sensors for Home Assistant.

---

## Sensors

### Clear-Sky DHI
**Diffuse Horizontal Irradiance (DHI):**
The portion of solar radiation that reaches the earth indirectly due to scattering by water vapor, aerosols, and clouds.

**Unit:** Watts per square meter (W/m²).

### Clear-Sky DNI
**Direct Normal Irradiance (DNI):**
The portion of solar radiation that reaches the earth directly from the sun.

**Unit:** Watts per square meter (W/m²).

### Clear-Sky GHI
**Global Horizontal Irradiance (GHI):**
The total solar radiation per unit area measured on a horizontal surface on the earth. GHI is the sum of two components:
- Direct Normal Irradiance (DNI)
- Diffuse Horizontal Irradiance (DHI)

**Formula:**
![GHI Formula](https://latex.codecogs.com/svg.image?\pagecolor{white}\text{GHI}=\text{DHI}+(\text{DNI}\cdot\cos(\alpha_{\text{zenith}})))

**Unit:** Watts per square meter (W/m²).

---

## Model

Values come from the [Ineichen-Perez](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.ineichen.html) clear-sky model, implemented in pure Python (pvlib can't be installed on Home Assistant OS). It matches pvlib's implementation to within 0.5 W/m² for GHI and DHI and 2 W/m² for DNI, in every hour of a year at the test sites.

The model's accuracy depends on site altitude and Linke turbidity (atmospheric haze, typically 2–5). The integration uses the home location and elevation from Home Assistant's settings (**Settings → System → General**), and a typical turbidity of 3.0.

---

## Usage

Go to **Settings → Devices & services → Add integration**, choose **Clear-Sky Solar**, and select **Submit**. There is nothing to configure.

---

## Installation

Requires Home Assistant 2026.10 or newer.

### Using [HACS](https://hacs.xyz/) (Recommended)
1. Open HACS in Home Assistant.
2. Open the menu (⋮) and choose **Custom repositories**.
3. Add `https://github.com/lymanepp/ha-clear-sky-solar` with type **Integration**.
4. Search for **Clear-Sky Solar** and download it.
5. Restart Home Assistant.

### Manual Installation
1. Download `clear_sky_solar.zip` from the [latest release](https://github.com/lymanepp/ha-clear-sky-solar/releases/latest).
2. Extract it into `custom_components/clear_sky_solar/` inside your Home Assistant configuration directory (the folder that contains `configuration.yaml`).
3. Restart Home Assistant.

---

## Additional Notes

- Check the [project repository](https://github.com/lymanepp/ha-clear-sky-solar) for updates or troubleshooting information.

---

## License

[AGPL-3.0](LICENSE.md)
