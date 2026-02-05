import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

from spots import SURF_SPOTS
from weather_api import get_current_by_coords, geocode_city, WeatherAPIError
from marine_api import get_marine_hourly, MarineAPIError
from scoring import add_scores, best_hours
from utils import israel_time_now, time_from_utc_offset, deg_to_compass, wind_relation_to_beach
from favorites import load_favorites, toggle_favorite
from extras_api import get_extras, ExtrasAPIError
from surfers_api import build_top_surfers, get_wiki_summary, SurferAPIError


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Surf & Weather Dashboard", page_icon="🌊", layout="wide")
st.title("🌊 Surf & Weather Dashboard")

API_KEY = st.secrets["api_key"]

# -----------------------------
# Sidebar (simple)
# -----------------------------
st.sidebar.header("Controls")
mode = st.sidebar.radio("Choose", ["Surf Spots (Map)", "City Search"], index=0)
units = st.sidebar.selectbox("Units", ["metric", "imperial"], index=0)
level = st.sidebar.selectbox("Surf level", ["Beginner", "Intermediate", "Advanced"], index=1)

st.sidebar.divider()
st.sidebar.caption(f"🇮🇱 Israel time now: {israel_time_now()}")

# -----------------------------
# Helpers
# -----------------------------
def marine_to_df(marine_json: dict, beach_facing_deg: float) -> pd.DataFrame:
    h = marine_json.get("hourly", {})
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(h.get("time", [])),
            "wave_height": h.get("wave_height", []),
            "wave_period": h.get("wave_period", []),
            "wave_dir_deg": h.get("wave_direction", []),
            "wind_speed": h.get("wind_speed_10m", []),
            "wind_dir_deg": h.get("wind_direction_10m", []),
        }
    )
    if df.empty:
        return df

    df["wave_dir"] = df["wave_dir_deg"].apply(lambda d: deg_to_compass(float(d)) if d is not None else "")
    df["wind_dir"] = df["wind_dir_deg"].apply(lambda d: deg_to_compass(float(d)) if d is not None else "")

    def _rel(d):
        if d is None:
            return ("", "")
        rel, color = wind_relation_to_beach(float(d), beach_facing_deg)
        return rel, color

    rels = df["wind_dir_deg"].apply(_rel)
    df["wind_relation"] = rels.apply(lambda t: t[0])
    df["wind_relation_color"] = rels.apply(lambda t: t[1])

    return df


@st.cache_data(ttl=600)
def fetch_all(lat: float, lon: float, units: str):
    current = get_current_by_coords(lat, lon, API_KEY, units=units)
    marine = get_marine_hourly(lat, lon)
    extras = get_extras(lat, lon)
    return current, marine, extras


def spot_names_favorites_first() -> list[str]:
    all_names = [s["name"] for s in SURF_SPOTS]
    favs = load_favorites()
    fav_first = [n for n in favs if n in all_names]
    rest = [n for n in all_names if n not in fav_first]
    return fav_first + rest


# -----------------------------
# Selection (spot or city)
# -----------------------------
selected_name = None
lat = lon = None
beach_facing_deg = 270

if mode == "Surf Spots (Map)":
    st.subheader("🏖️ Choose a surf spot")

    spot_names = spot_names_favorites_first()
    if not spot_names:
        st.error("No surf spots found in spots.py")
        st.stop()

    selected_name = st.selectbox("Spot (favorites first)", spot_names, index=0)
    chosen = next(s for s in SURF_SPOTS if s["name"] == selected_name)
    lat, lon = chosen["lat"], chosen["lon"]
    beach_facing_deg = chosen.get("beach_facing_deg", 270)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("⭐ Toggle favorite"):
            toggle_favorite(selected_name)
            st.success("Favorite updated. (Refresh if needed)")
    with col2:
        st.caption("Favorites are stored locally in favorites.json (may reset on Streamlit Cloud).")

    # --- ONE MAP ONLY (favorites as golden dots) ---
    df_map = pd.DataFrame(SURF_SPOTS)
    favs = load_favorites()

    df_map["is_selected"] = df_map["name"].eq(selected_name)
    df_map["is_fav"] = df_map["name"].isin(favs)

    # Base dots: selected red, others blue
    df_map["base_color"] = df_map["is_selected"].apply(lambda x: [255, 0, 0, 220] if x else [0, 120, 255, 170])
    df_fav = df_map[df_map["is_fav"]].copy()

    layer_all = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position="[lon, lat]",
        get_radius=260,
        get_fill_color="base_color",
        get_line_color="[255,255,255]",
        line_width_min_pixels=1,
        pickable=True,
    )

    layer_favs = pdk.Layer(
        "ScatterplotLayer",
        data=df_fav,
        get_position="[lon, lat]",
        get_radius=330,
        get_fill_color="[255, 215, 0, 220]",  # gold
        get_line_color="[255,255,255]",
        line_width_min_pixels=1,
        pickable=False,
    )

    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=9)
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer_all, layer_favs],
            initial_view_state=view_state,
            tooltip={"text": "{name}"},
        )
    )
    st.caption("🗺️ Map legend: 🔴 Selected • 🟡 Favorite • 🔵 Other")

else:
    st.subheader("🌍 Search by city (auto-lat/lon)")

    city = st.text_input("City", value="Tel Aviv")
    if st.button("Find city"):
        try:
            matches = geocode_city(city.strip(), API_KEY, limit=5)
            if not matches:
                st.error("No matches found. Try a different spelling.")
                st.stop()

            options = [
                f"{m.get('name')}, {m.get('state','')} {m.get('country')} (lat={m['lat']:.2f}, lon={m['lon']:.2f})"
                for m in matches
            ]
            choice = st.selectbox("Select location", options, index=0)
            m = matches[options.index(choice)]

            selected_name = f"{m.get('name')} ({m.get('country')})"
            lat, lon = m["lat"], m["lon"]

            st.success(f"Selected: {selected_name}")
            st.caption("Tip: For surf scoring, use Surf Spots mode (it includes beach facing direction).")

        except Exception as e:
            st.error("Geocoding failed.")
            st.caption(str(e))
            st.stop()

if lat is None or lon is None:
    st.info("Select a surf spot or search a city to load data.")
    st.stop()

# -----------------------------
# Fetch data
# -----------------------------
try:
    with st.spinner("Fetching weather + marine + extras..."):
        current, marine, extras = fetch_all(lat, lon, units)
except WeatherAPIError as e:
    st.error(f"OpenWeather error: {e}")
    st.stop()
except MarineAPIError as e:
    st.error(f"Marine API error: {e}")
    st.stop()
except ExtrasAPIError as e:
    st.error(f"Extras API error: {e}")
    st.stop()
except Exception as e:
    st.error("Unexpected error")
    st.caption(str(e))
    st.stop()

# -----------------------------
# Time info
# -----------------------------
city_time = time_from_utc_offset(int(current["timezone"]))
st.info(f"🕒 🇮🇱 Israel time: **{israel_time_now()}**    |    🌍 Local time here: **{city_time}**")

# -----------------------------
# Dashboard overview (wide, with emojis)
# -----------------------------
st.subheader(f"📍 Overview — {current['name']}, {current['sys']['country']}")

temp_sym = "°F" if units == "imperial" else "°C"
wind_sym = "mph" if units == "imperial" else "m/s"

desc = current["weather"][0]["description"]
icon = current["weather"][0]["icon"]
wind_speed_now = current["wind"]["speed"]
wind_dir_now = deg_to_compass(current["wind"].get("deg", 0))

daily = extras.get("daily", {})
hourly = extras.get("hourly", {})

sunrise = (daily.get("sunrise") or ["—"])[0]
sunset = (daily.get("sunset") or ["—"])[0]

uv_now = (hourly.get("uv_index") or [None])[0]
rad_now = (hourly.get("shortwave_radiation") or [None])[0]  # W/m²
vis_now = (hourly.get("visibility") or [None])[0]  # meters
cloud_now = (hourly.get("cloud_cover") or [None])[0]  # %
prec_now = (hourly.get("precipitation") or [None])[0]  # mm
t2m_now = (hourly.get("temperature_2m") or [None])[0]  # °C

# row 1: essentials
r1 = st.columns(6)
r1[0].image(f"https://openweathermap.org/img/wn/{icon}@2x.png", width=70)
r1[0].caption(f"**{desc}**")

r1[1].metric("🌡️ Temp", f"{current['main']['temp']}{temp_sym}")
r1[2].metric("🤒 Feels like", f"{current['main']['feels_like']}{temp_sym}")
r1[3].metric("💧 Humidity", f"{current['main']['humidity']}%")
r1[4].metric("💨 Wind", f"{wind_speed_now} {wind_sym}")
r1[5].metric("🧭 Wind dir", f"{wind_dir_now}")

# row 2: extras
r2 = st.columns(6)
r2[0].metric("📏 2m Temp", f"{t2m_now}°C" if t2m_now is not None else "—")
r2[1].metric("☀️ UV", f"{uv_now}" if uv_now is not None else "—")
r2[2].metric("🔆 Radiation", f"{rad_now} W/m²" if rad_now is not None else "—")
r2[3].metric("👀 Visibility", f"{int(vis_now / 1000)} km" if vis_now is not None else "—")
r2[4].metric("☁️ Cloud", f"{cloud_now}%" if cloud_now is not None else "—")
r2[5].metric("🌧️ Precip", f"{prec_now} mm" if prec_now is not None else "—")

st.caption(f"🌅 Sunrise: {sunrise}   |   🌇 Sunset: {sunset}")

# -----------------------------
# Marine + scoring
# -----------------------------
df_marine = marine_to_df(marine, beach_facing_deg)
if df_marine.empty:
    st.warning("No marine data available for this location.")
    st.stop()

df_scored = add_scores(df_marine, level=level)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🏄 Best Hours", "📈 Charts", "📋 Tables"])

with tab1:
    st.subheader(f"✅ Recommended hours (level: {level})")
    st.dataframe(best_hours(df_scored, top_n=6), use_container_width=True)
    st.markdown("**Wind relation:** 🟢 Offshore • 🟡 Cross • 🔴 Onshore")

with tab2:
    cA, cB = st.columns(2)
    with cA:
        st.plotly_chart(px.line(df_scored, x="time", y="wave_height", title="🌊 Wave height (m)"),
                        use_container_width=True)
    with cB:
        st.plotly_chart(px.line(df_scored, x="time", y="wave_period", title="⏱️ Wave period (s)"),
                        use_container_width=True)

    cC, cD = st.columns(2)
    with cC:
        st.plotly_chart(px.line(df_scored, x="time", y="wind_speed", title="💨 Wind speed (hourly)"),
                        use_container_width=True)
    with cD:
        st.plotly_chart(px.line(df_scored, x="time", y="surf_score", title="🏄 Surf score (0-100)"),
                        use_container_width=True)

with tab3:
    show = df_scored.head(48).copy()
    show["relation"] = show["wind_relation_color"] + " " + show["wind_relation"]
    st.dataframe(show, use_container_width=True)

st.divider()
st.subheader("🏆 Top Surfers (Legends) — powered by Wikipedia")

@st.cache_data(ttl=86400)
def fetch_surfers_cards():
    cards = []
    for s in build_top_surfers():
        data = get_wiki_summary(s["wiki_title"])
        thumb = None
        if isinstance(data.get("thumbnail"), dict):
            thumb = data["thumbnail"].get("source")

        cards.append({
            "name": s["name"],
            "known_for": s["known_for"],
            "extract": data.get("extract", "No summary available."),
            "thumb": thumb,
            "wiki_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        })
    return cards

try:
    cards = fetch_surfers_cards()
    cols = st.columns(3)
    for i, card in enumerate(cards):
        with cols[i]:
            if card["thumb"]:
                st.image(card["thumb"], use_container_width=True)
            st.markdown(f"### 🏄 {card['name']}")
            st.caption(card["known_for"])
            st.write(card["extract"])
            if card["wiki_url"]:
                st.link_button("Open Wikipedia", card["wiki_url"])
except SurferAPIError as e:
    st.warning("Could not load surfers info from Wikipedia right now.")
    st.caption(str(e))