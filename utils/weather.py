import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(location: str):
    """
    Current weather for the location.
    """
    demo_scenarios = {
        "moradabad": {"rain_prob": 78, "humidity": 82, "temperature": 30},
        "mumbai": {"rain_prob": 10, "humidity": 85, "temperature": 32},
        "uttarakhand": {"rain_prob": 15, "humidity": 40, "temperature": 22}
    }
    
    defaults = {"rain_prob": 45, "humidity": 60, "temperature": 28, "location": location}
    
    if not API_KEY or "YOUR_API_KEY" in API_KEY:
        res = demo_scenarios.get(location.lower(), defaults)
        res["location"] = location
        res["source"] = "fallback"
        return res

    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
        geo_resp = requests.get(geo_url, timeout=3).json()
        if not geo_resp: return {**defaults, "location": location}
        
        lat, lon = geo_resp[0]["lat"], geo_resp[0]["lon"]
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        w_resp = requests.get(url, timeout=3).json()
        
        main_weather = w_resp.get("weather", [{}])[0].get("main", "").lower()
        rain_prob = 90 if "rain" in main_weather else (70 if "drizzle" in main_weather else (30 if "clouds" in main_weather else 5))

        return {
            "location": location,
            "rain_prob": rain_prob,
            "humidity": w_resp.get("main", {}).get("humidity", 50),
            "temperature": w_resp.get("main", {}).get("temp", 25),
            "source": "live"
        }
    except:
        return {**defaults, "location": location, "source": "fallback"}

def get_forecast(location: str):
    """
    5-day weather forecast summary.
    """
    if not API_KEY or "YOUR_API_KEY" in API_KEY:
        return [
            {"day": "Day 1", "temp": 28, "status": "Sunny"},
            {"day": "Day 2", "temp": 27, "status": "Clear"},
            {"day": "Day 3", "temp": 29, "status": "Partly Cloudy"},
            {"day": "Day 4", "temp": 30, "status": "Sunny"},
            {"day": "Day 5", "temp": 26, "status": "Rainy"}
        ]

    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
        geo_resp = requests.get(geo_url, timeout=3).json()
        if not geo_resp: return []
        
        lat, lon = geo_resp[0]["lat"], geo_resp[0]["lon"]
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        f_resp = requests.get(url, timeout=3).json()
        
        forecast = []
        for i in range(0, 40, 8): # Every 24 hours (8 intervals of 3h)
            item = f_resp['list'][i]
            forecast.append({
                "day": item['dt_txt'].split(" ")[0],
                "temp": item['main']['temp'],
                "status": item['weather'][0]['main']
            })
        return forecast
    except:
        return []
