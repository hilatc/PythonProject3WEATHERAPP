from __future__ import annotations
from datetime import datetime, timezone, timedelta
import math

def israel_time_now() -> str:
    tz_israel = timezone(timedelta(hours=3))  # UTC+3 (good enough for project)
    return datetime.now(tz_israel).strftime("%A, %d %b %Y • %H:%M")

def time_from_utc_offset(offset_seconds: int) -> str:
    tz = timezone(timedelta(seconds=int(offset_seconds)))
    return datetime.now(tz).strftime("%A, %d %b %Y • %H:%M")

def deg_to_compass(deg: float) -> str:
    directions = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    ix = int((deg % 360) / 22.5)
    return directions[ix]

def safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def _angle_diff(a: float, b: float) -> float:
    d = (a - b) % 360
    return min(d, 360 - d)

def wind_relation_to_beach(wind_from_deg: float, beach_facing_deg: float) -> tuple[str, str]:
    onshore_from = beach_facing_deg % 360
    offshore_from = (beach_facing_deg + 180) % 360

    d_off = _angle_diff(wind_from_deg, offshore_from)
    d_on = _angle_diff(wind_from_deg, onshore_from)

    if d_off <= 45:
        return "Offshore", "🟢"
    if d_on <= 45:
        return "Onshore", "🔴"
    return "Cross", "🟡"
