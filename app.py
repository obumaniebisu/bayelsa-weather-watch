import streamlit as st
import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"
CITY = "Yenagoa"
COUNTRY_CODE = "NG"

st.title("Bayelsa Weather Watch")
st.subheader("Current Weather in Yenagoa, Bayelsa, Nigeria")

api_key = st.text_input("Enter your OpenWeatherMap API key:", type="password")

if api_key:
    params = {
        "q": f"{CITY},{COUNTRY_CODE}",
        "appid": api_key,
        "units": "metric",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            temperature = data.get("main", {}).get("temp")
            humidity = data.get("main", {}).get("humidity")

            if temperature is not None and humidity is not None:
                col1, col2 = st.columns(2)
                col1.metric("🌡️ Temperature", f"{temperature} °C")
                col2.metric("💧 Humidity", f"{humidity} %")
            else:
                st.error("Unexpected response structure from the weather API.")
        elif response.status_code == 401:
            st.error("Invalid API key. Please check your OpenWeatherMap API key.")
        elif response.status_code == 404:
            st.error("City not found. Please check the city name.")
        else:
            st.error(f"Error fetching weather data (status code: {response.status_code}).")
    except requests.exceptions.Timeout:
        st.error("The request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the weather service. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching weather data: {e}")
else:
    st.info("Please enter your OpenWeatherMap API key above to fetch weather data.")
