import requests

BASE_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
BASE_GEO = "https://api.openweathermap.org/geo/1.0/direct"


class WeatherAPIError(Exception):
    pass


def geocode_city(city: str, api_key: str, limit: int = 5) -> list[dict]:
    """
    Convert city name -> list of possible locations with lat/lon
    """
    params = {
        "q": city,
        "appid": api_key,
        "limit": limit,
    }
    r = requests.get(BASE_GEO, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def get_current_by_city(city: str, api_key: str, units: str = "metric") -> dict:
    """
    Current weather by city name
    """
    params = {
        "q": city,
        "appid": api_key,
        "units": units,
    }
    r = requests.get(BASE_CURRENT, params=params, timeout=15)
    data = r.json()
    if str(data.get("cod")) != "200":
        raise WeatherAPIError(data.get("message", "Weather API error"))
    return data


def get_current_by_coords(lat: float, lon: float, api_key: str, units: str = "metric") -> dict:
    """
    Current weather by latitude / longitude
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
    }
    r = requests.get(BASE_CURRENT, params=params, timeout=15)
    data = r.json()
    if str(data.get("cod")) != "200":
        raise WeatherAPIError(data.get("message", "Weather API error"))
    return data

