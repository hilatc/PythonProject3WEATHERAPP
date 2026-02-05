import requests

BASE_MARINE = "https://marine-api.open-meteo.com/v1/marine"


class MarineAPIError(Exception):
    pass


def get_marine_hourly(lat: float, lon: float) -> dict:
    """
    Fetch hourly marine forecast:
    - wave height
    - wave period
    - wave direction
    - wind speed
    - wind direction
    From Open-Meteo Marine API (no API key required)
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wave_height,wave_period,wave_direction,wind_speed_10m,wind_direction_10m",
        "timezone": "auto",
    }

    r = requests.get(BASE_MARINE, params=params, timeout=20)
    if r.status_code != 200:
        raise MarineAPIError("Marine API error")

    return r.json()
