"""Utility functions for Bayelsa Weather Watch."""


def calculate_heat_index(temp_c: float, humidity: float) -> float:
    """Calculate the Heat Index (Real Feel) in Celsius.

    Uses the Rothfusz regression formula (originally in Fahrenheit),
    then converts the result back to Celsius.

    Args:
        temp_c: Ambient air temperature in degrees Celsius.
        humidity: Relative humidity as a percentage (0–100).

    Returns:
        Heat index in degrees Celsius, rounded to one decimal place.
    """
    temp_f = temp_c * 9 / 5 + 32

    hi_f = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * humidity
        - 0.22475541 * temp_f * humidity
        - 0.00683783 * temp_f ** 2
        - 0.05481717 * humidity ** 2
        + 0.00122874 * temp_f ** 2 * humidity
        + 0.00085282 * temp_f * humidity ** 2
        - 0.00000199 * temp_f ** 2 * humidity ** 2
    )

    hi_c = (hi_f - 32) * 5 / 9
    return round(hi_c, 1)


def assess_flood_risk(rainfall_mm: float, humidity: float) -> dict:
    """Assess flood risk for a Bayelsa LGA based on rainfall and humidity.

    Args:
        rainfall_mm: Rainfall in the last hour in millimeters (from the
                     OpenWeatherMap ``rain.1h`` field; use 0 if absent).
        humidity: Relative humidity as a percentage (0–100).

    Returns:
        A dict with keys:
          - ``level``   : str  — "Low", "Moderate", "High", or "Critical"
          - ``message`` : str  — Human-readable alert text
          - ``color``   : str  — Hex colour for the UI callout
    """
    high_humidity = humidity > 85

    if rainfall_mm >= 20 and high_humidity:
        return {
            "level": "Critical",
            "message": (
                "⚠️ CRITICAL FLOOD RISK: Heavy rainfall combined with very high "
                "humidity. Residents in low-lying areas should move to higher ground "
                "immediately. Monitor official Bayelsa State emergency broadcasts."
            ),
            "color": "#B71C1C",
        }
    elif rainfall_mm >= 10 or (rainfall_mm >= 5 and high_humidity):
        return {
            "level": "High",
            "message": (
                "🔴 HIGH FLOOD RISK: Significant rainfall detected. Avoid waterways "
                "and flood-prone areas. Stay alert for further updates."
            ),
            "color": "#E53935",
        }
    elif rainfall_mm >= 2 or high_humidity:
        return {
            "level": "Moderate",
            "message": (
                "🟡 MODERATE FLOOD RISK: Some rainfall and/or very high humidity. "
                "Exercise caution near drainage channels and low-lying roads."
            ),
            "color": "#F9A825",
        }
    else:
        return {
            "level": "Low",
            "message": (
                "🟢 LOW FLOOD RISK: Current conditions are within normal range. "
                "No immediate flood threat detected."
            ),
            "color": "#2E7D32",
        }
