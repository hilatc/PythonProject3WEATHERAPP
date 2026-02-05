import requests

BASE_FORECAST = "https://api.open-meteo.com/v1/forecast"


class ExtrasAPIError(Exception):
    pass


def get_extras(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "hourly": "uv_index,shortwave_radiation,visibility,cloud_cover,precipitation,temperature_2m",
        "daily": "sunrise,sunset",
    }
    r = requests.get(BASE_FORECAST, params=params, timeout=20)
    if r.status_code != 200:
        raise ExtrasAPIError("Extras API error")
    return r.json()
