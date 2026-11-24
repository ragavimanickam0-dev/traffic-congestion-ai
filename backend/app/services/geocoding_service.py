import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger("trafficintel.geocoding")

_GEOCODE_CACHE: Dict[str, List[Dict]] = {}
_REVERSE_CACHE: Dict[str, Dict] = {}

NOMINATIM_HEADERS = {
    "User-Agent": "TrafficIntel-AI-Mobility-Platform/1.0 (contact: support@trafficintel.ai)"
}

def search_locations(query: str, limit: int = 5) -> List[Dict]:
    clean_query = query.strip()
    if not clean_query:
        return []

    cache_key = f"{clean_query.lower()}_{limit}"
    if cache_key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[cache_key]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": clean_query,
        "format": "json",
        "addressdetails": 1,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params, headers=NOMINATIM_HEADERS, timeout=6)
        if response.status_code == 200:
            data = response.json()
            results = [
                {
                    "display_name": item.get("display_name", "Unknown Area"),
                    "lat": float(item.get("lat")),
                    "lon": float(item.get("lon")),
                    "type": item.get("type", "way")
                }
                for item in data
                if "lat" in item and "lon" in item
            ]
            _GEOCODE_CACHE[cache_key] = results
            return results
    except Exception as e:
        logger.warning("Nominatim query error: %s", e)

    defaults = [
        {"display_name": f"{clean_query} Central", "lat": 12.9716, "lon": 77.5946, "type": "city"},
        {"display_name": f"{clean_query} Transit Hub", "lat": 12.9772, "lon": 77.5708, "type": "junction"},
        {"display_name": f"{clean_query} Tech Corridor", "lat": 12.9352, "lon": 77.6245, "type": "commercial"}
    ]
    return defaults

def reverse_geocode(lat: float, lon: float) -> Optional[Dict]:
    cache_key = f"{round(lat, 4)}_{round(lon, 4)}"
    if cache_key in _REVERSE_CACHE:
        return _REVERSE_CACHE[cache_key]

    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json"}

    try:
        response = requests.get(url, params=params, headers=NOMINATIM_HEADERS, timeout=6)
        if response.status_code == 200:
            data = response.json()
            res = {
                "display_name": data.get("display_name", f"Position ({lat:.3f}, {lon:.3f})"),
                "lat": lat,
                "lon": lon
            }
            _REVERSE_CACHE[cache_key] = res
            return res
    except Exception as e:
        logger.warning("Reverse geocode error: %s", e)

    return {"display_name": f"Area ({lat:.3f}, {lon:.3f})", "lat": lat, "lon": lon}
