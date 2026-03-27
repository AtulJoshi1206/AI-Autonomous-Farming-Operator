import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def test():
    print(f"Testing API Key: {API_KEY[:4]}...{API_KEY[-4:]}")
    location = "Moradabad"
    
    # Test Geocoding
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    try:
        geo_resp = requests.get(geo_url, timeout=5)
        print(f"Geocoding Status: {geo_resp.status_code}")
        if geo_resp.status_code == 200:
            data = geo_resp.json()
            if data:
                print(f"Geocoding Success! Lat: {data[0]['lat']}, Lon: {data[0]['lon']}")
                
                # Test Weather
                w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={data[0]['lat']}&lon={data[0]['lon']}&appid={API_KEY}&units=metric"
                w_resp = requests.get(w_url, timeout=5)
                print(f"Weather Status: {w_resp.status_code}")
                if w_resp.status_code == 200:
                    print("Weather Success!")
                    print(w_resp.json().get("main"))
                else:
                    print(f"Weather Failure: {w_resp.text}")
            else:
                print("Geocoding returned empty list.")
        else:
            print(f"Geocoding Failure: {geo_resp.text}")
    except Exception as e:
        print(f"Test Error: {e}")

if __name__ == "__main__":
    test()
