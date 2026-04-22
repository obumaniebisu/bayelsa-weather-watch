import os
import pathlib

import requests
import streamlit as st
from dotenv import load_dotenv

from utils import assess_flood_risk, calculate_heat_index

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

API_URL = "https://api.openweathermap.org/data/2.5/weather"
COUNTRY_CODE = "NG"

BAYELSA_LGAS = [
    "Yenagoa",
    "Brass",
    "Sagbama",
    "Ogbia",
    "Ekeremor",
    "Nembe",
    "Kolokuma/Opokuma",
    "Southern Ijaw",
]

# ---------------------------------------------------------------------------
# Page setup & CSS injection
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Bayelsa Weather Watch",
    page_icon="🌦️",
    layout="wide",
)

_css_path = pathlib.Path(__file__).parent / "style.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🌿 Bayelsa Weather Watch")
    st.markdown("---")
    selected_lga = st.selectbox(
        "📍 Select LGA",
        BAYELSA_LGAS,
        index=0,
        help="Choose a Local Government Area in Bayelsa State.",
    )
    st.markdown("---")
    st.markdown(
        "<small>Data powered by [OpenWeatherMap](https://openweathermap.org/).</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title(f"🌦️ Bayelsa Weather Watch")
st.subheader(f"Current Weather — {selected_lga}, Bayelsa State, Nigeria")
st.markdown("---")

# Resolve API key: environment variable takes priority; fallback to user input.
api_key = os.getenv("WEATHER_API_KEY", "")
if not api_key:
    api_key = st.text_input(
        "🔑 Enter your OpenWeatherMap API key (or set WEATHER_API_KEY env var):",
        type="password",
    )

if api_key:
    # Build query — replace slash with space for Kolokuma/Opokuma
    city_query = selected_lga.replace("/", " ")
    params = {
        "q": f"{city_query},{COUNTRY_CODE}",
        "appid": api_key,
        "units": "metric",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            main = data.get("main", {})
            rain = data.get("rain", {})

            temperature = main.get("temp")
            humidity = main.get("humidity")
            rainfall_mm = rain.get("1h", 0.0)

            if temperature is not None and humidity is not None:
                # Compute heat index as the "real feel" override
                heat_index = calculate_heat_index(temperature, humidity)

                # Three-column metric display
                col1, col2, col3 = st.columns(3)
                col1.metric("🌡️ Temperature", f"{temperature} °C")
                col2.metric(
                    "🤔 Feels Like (Heat Index)",
                    f"{heat_index} °C",
                    delta=f"{round(heat_index - temperature, 1)} °C vs air temp",
                )
                col3.metric("💧 Humidity", f"{humidity} %")

                st.markdown("---")

                # ── Local Alert section ────────────────────────────────────
                st.subheader("🚨 Local Alert")
                risk = assess_flood_risk(rainfall_mm, humidity)

                st.markdown(
                    f"""
                    <div style="
                        background-color: {risk['color']}22;
                        border-left: 5px solid {risk['color']};
                        border-radius: 10px;
                        padding: 1rem 1.25rem;
                        font-size: 1rem;
                        font-weight: 500;
                        line-height: 1.6;
                        margin-top: 0.5rem;
                        color: #E0E0E0;
                    ">
                        <strong>Flood Risk Level: {risk['level']}</strong><br>{risk['message']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if rainfall_mm > 0:
                    st.caption(f"🌧️ Rainfall (last hour): {rainfall_mm} mm")
                else:
                    st.caption("🌧️ No rainfall recorded in the last hour.")

            else:
                st.error("Unexpected response structure from the weather API.")

        elif response.status_code == 401:
            st.error("❌ Invalid API key. Please check your OpenWeatherMap API key.")
        elif response.status_code == 404:
            st.warning(
                f"⚠️ '{selected_lga}' was not found in the weather database. "
                "Try a nearby city or check the LGA name spelling."
            )
        else:
            st.error(
                f"Error fetching weather data (status code: {response.status_code})."
            )

    except requests.exceptions.Timeout:
        st.error("⏱️ The request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error(
            "🔌 Could not connect to the weather service. "
            "Check your internet connection."
        )
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching weather data: {e}")
else:
    st.info(
        "👆 Please enter your OpenWeatherMap API key above, "
        "or set the **WEATHER_API_KEY** environment variable to fetch weather data."
    )
