import streamlit as st

st.title('Weather App')

name = st.text_input('Enter your name', '')
if name:
    st.write(f'Hello {name}, welcome to the weather app!')
    # Weather Checker App 🌤️

    Streamlit
    app
    that
    fetches
    current
    weather + 5 - day
    forecast
    from OpenWeatherMap
    and displays
    an
    interactive
    temperature
    forecast
    graph.

    ## Features
    - REST
    API
    calls
    to
    OpenWeatherMap
    - Current
    weather(temp, feels_like, humidity, wind, description + icon)
    - 5 - day
    forecast + interactive
    Plotly
    graph
    - Secrets
    stored
    safely in `.streamlit / secrets.toml
    `

    ## Run locally
    1.
    Install
    dependencies:
    ```bash
    pip
    install - r
    requirements.txt
