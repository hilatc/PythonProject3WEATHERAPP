# 🌊 Surf & Weather Dashboard (Streamlit)

A Python + Streamlit dashboard that combines **current weather**, **marine forecast**, and **surf scoring** to help users choose the best hours to surf.

## ✅ Features
- **Surf Spots Map (pydeck)**  
  - Selected spot (🔴), favorites (🟡), other spots (🔵)
  - Favorites appear first in the spot list
- **City Search (OpenWeather Geocoding)**
- **Current Weather (OpenWeather REST API)**
  - temperature, feels-like, humidity, wind speed + wind direction
- **Marine Forecast (Open-Meteo Marine API)**
  - wave height, wave period, wave direction
  - wind speed + wind direction (hourly)
- **Extras (Open-Meteo)**
  - UV index, solar radiation, visibility, cloud cover, precipitation, sunrise/sunset
- **Surf Scoring (Beginner / Intermediate / Advanced)**
  - the level changes the scoring logic and recommended hours
- **Charts & Tables**
  - interactive Plotly graphs + raw forecast table
- **Extra Data Source**
  - “Top Surf Legends” cards using Wikipedia REST API (with User-Agent)

## 🧠 Business / UX Perspective
This dashboard is designed for surfers who want a quick decision tool:
- pick a beach (or search a city)
- choose skill level
- instantly see the best hours + trends (wind/waves/score)

## 🛠️ Tech Stack
- Python
- Streamlit
- REST APIs:
  - OpenWeather (weather + geocoding)
  - Open-Meteo Marine (waves + wind)
  - Open-Meteo Extras (UV/radiation/visibility/daylight)
  - Wikipedia REST API (surfer legends cards)
- Plotly (interactive charts)
- PyDeck (interactive map)
- Pandas (dataframes)

## 📁 Project Structure
