import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone, timedelta
def format_city_time(city_timezone_seconds: int) -> str:
    """
    OpenWeather returns timezone offset from UTC in seconds.
    Example: Israel is usually +7200 seconds (UTC+2), summer +10800 (UTC+3).
    """
    city_tz = timezone(timedelta(seconds=city_timezone_seconds))
    now_city = datetime.now(city_tz)
    return now_city.strftime("%A, %d %b %Y • %H:%M")

st.title("🌤️ Weather Checker")

API_KEY = st.secrets["api_key"]

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=15)
    return r.json()

def get_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=15)
    return r.json()

def forecast_to_df(forecast_json):
    rows = []
    for item in forecast_json["list"]:
        rows.append({
            "datetime": item["dt_txt"],
            "temp": item["main"]["temp"],
            "humidity": item["main"]["humidity"],
            "description": item["weather"][0]["description"]
        })
    df = pd.DataFrame(rows)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df

city = st.text_input("Enter a city", value="Tel Aviv")

if city:
    data = get_weather(city)

    if "main" in data:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        now_local = datetime.now().strftime("%A, %d %b %Y • %H:%M")
        city_time = format_city_time(data["timezone"])

        st.info(
            f"🧍 Your local time: **{now_local}**\n\n"
            f"🌍 Local time in {data['name']}: **{city_time}**"
        )

        st.write(f"🌡️ Temperature: {temp}°C")
        st.write(f"☁️ Weather: {desc}")
        st.write(f"💧 Humidity: {humidity}%")
    else:
        st.error("City not found. Try again.")
        st.stop()

    forecast_json = get_forecast(city)
    df = forecast_to_df(forecast_json)

    fig = px.line(df, x="datetime", y="temp", title="5-Day Temperature Forecast")
    st.plotly_chart(fig, use_container_width=True)

    st.write("Forecast table (first 20 rows):")
    st.dataframe(df.head(20), use_container_width=True)
