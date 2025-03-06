from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# OpenWeatherMap API Key
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_temperature(query):
    """Fetch temperature data from OpenWeatherMap"""
    params = {
        "appid": API_KEY,
        "units": "metric"  # Celsius
    }

    if isinstance(query, tuple):  # If (lat, lon)
        params.update({"lat": query[0], "lon": query[1]})
    else:  # If city or country
        params.update({"q": query})

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"]
    else:
        return None

@app.route("/temperature", methods=["GET"])
def fetch_temperature():
    """API endpoint to get temperature"""
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    city = request.args.get("city")
    country = request.args.get("country")

    if lat and lng:
        temp = get_temperature((lat, lng))
    elif city:
        temp = get_temperature(city)
    elif country:
        temp = get_temperature(country)
    else:
        return jsonify({"error": "Provide lat/lng, city, or country"}), 400

    if temp is not None:
        return jsonify({"temperature": f"{temp}°C"})
    else:
        return jsonify({"error": "Location not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
