import streamlit as st
import requests
import openai
import datetime

import os
from dotenv import load_dotenv
load_dotenv()

# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, weather_api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?appid={weather_api_key}&q={city}"
    response = requests.get(complete_url)
    return response.json()

def get_weekly_forecast(weather_api_key, lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/"
    complete_url = f"{base_url}forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(complete_url)
    return response.json()

# Weather icons mapping
WEATHER_ICONS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "haze": "🌫️",
    "drizzle": "🌦️"
}

def get_weather_icon(description):
    for key in WEATHER_ICONS:
        if key in description.lower():
            return WEATHER_ICONS[key]
    return "🌤️"

def display_weekly_forecast(data):
    try:
        st.subheader("7-Day Forecast", divider="rainbow")
        displayed_dates = set()
        
        # Create columns for the forecast
        cols = st.columns(7)
        col_index = 0
        
        for day in data['list']:
            date = datetime.datetime.fromtimestamp(day['dt']).strftime('%A')
            if date not in displayed_dates and len(displayed_dates) < 7:
                displayed_dates.add(date)
                with cols[col_index]:
                    temp = day['main']['temp'] - 273.15
                    icon = get_weather_icon(day['weather'][0]['description'])
                    st.markdown(f"**{date}**")
                    st.markdown(f"{icon}")
                    st.markdown(f"**{temp:.1f}°C**")
                    st.caption(f"{day['weather'][0]['description'].capitalize()}")
                    col_index += 1
                    
    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))

def main():
    # Page configuration
    st.set_page_config(page_title="SkySync", page_icon="🌤️", layout="centered")

    # Sidebar configuration
    with st.sidebar:
        st.image("cloud.jpg", width=120)
        st.title("SkySync 🌦️")
        st.markdown("---")
        city = st.text_input("Enter City name", "London")
        st.markdown("---")
        if st.button("Get Weather", use_container_width=True, type="primary"):
            st.session_state.get_weather = True
        else:
            if 'get_weather' not in st.session_state:
                st.session_state.get_weather = False

    # API keys
    weather_api_key =os.getenv("weather_api_key")
    openai_api_key = os.getenv("openai_api_key") 

    if st.session_state.get_weather:
        with st.spinner("🌤️ Gathering weather magic..."):
            weather_data = get_weather_data(city, weather_api_key)

            if weather_data.get("cod") != 404:
                # Current weather display
                st.header(f"Weather in {city.title()} ", divider="blue")
                
                # Main metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temperature 🌡️", 
                            f"{weather_data['main']['temp'] - 273.15:.1f}°C",
                            help="Current temperature")
                with col2:
                    st.metric("Humidity 💧", 
                            f"{weather_data['main']['humidity']}%",
                            help="Relative humidity")
                with col3:
                    st.metric("Wind Speed 🌬️", 
                            f"{weather_data['wind']['speed']} m/s",
                            help="Wind speed")
                
                # Weather description
                current_weather = weather_data['weather'][0]
                icon = get_weather_icon(current_weather['description'])
                st.markdown(f"""
                    <div style="background-color:#e6f3ff;padding:20px;border-radius:10px">
                        <h4 style="margin:0">{icon} {current_weather['description'].capitalize()}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                # Weekly forecast
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                forecast_data = get_weekly_forecast(weather_api_key, lat, lon)
                
                if forecast_data.get("cod") != "404":
                    display_weekly_forecast(forecast_data)
                
                # Additional details
                with st.expander("Advanced Details"):
                    cols = st.columns(2)
                    cols[0].metric("Pressure", f"{weather_data['main']['pressure']} hPa")
                    cols[1].metric("Visibility", f"{weather_data.get('visibility', 'N/A')}m")
                    cols[0].metric("Cloud Cover", f"{weather_data['clouds']['all']}%")
                    cols[1].metric("Feels Like", 
                                 f"{weather_data['main']['feels_like'] - 273.15:.1f}°C")
            else:
                st.error("City not found. Please try another location.")

if __name__ == "__main__":
    main()