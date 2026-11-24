import logging
import requests
from typing import Dict, Any

logger = logging.getLogger("trafficintel.weather")

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Rain showers",
    95: "Thunderstorm"
}

def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            w_code = current.get("weather_code", 0)
            condition = WMO_WEATHER_CODES.get(w_code, "Partly Cloudy")

            return {
                "latitude": lat,
                "longitude": lon,
                "temperature_c": float(current.get("temperature_2m", 24.0)),
                "humidity": int(current.get("relative_humidity_2m", 60)),
                "precipitation_mm": float(current.get("precipitation", 0.0)),
                "condition": condition,
                "wind_speed_kmh": float(current.get("wind_speed_10m", 10.0)),
                "provider": "Open-Meteo Real-Time Meteorological API",
                "is_live": True
            }
    except Exception as e:
        logger.warning("Weather query fallback: %s", e)

    return {
        "latitude": lat,
        "longitude": lon,
        "temperature_c": 25.0,
        "humidity": 65,
        "precipitation_mm": 0.0,
        "condition": "Mainly Clear",
        "wind_speed_kmh": 12.0,
        "provider": "Standard Meteorological Baseline",
        "is_live": False
    }
