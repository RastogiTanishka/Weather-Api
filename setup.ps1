# PowerShell script to set up the Flask weather API project

# Step 1: Create a new directory for the project
$projectName = "FlaskWeatherAPI"
$envFile = ".env"

Write-Host "Setting up project: $projectName" -ForegroundColor Green

# Check if the project folder exists, if not, create it
if (-Not (Test-Path $projectName)) {
    New-Item -ItemType Directory -Path $projectName
}

# Step 2: Navigate to the project folder
Set-Location -Path $projectName

# Step 3: Create a virtual environment
Write-Host "Creating a virtual environment..." -ForegroundColor Cyan
python -m venv venv

# Step 4: Activate the virtual environment
Write-Host "Activating the virtual environment..." -ForegroundColor Cyan
Set-ExecutionPolicy Unrestricted -Scope Process -Force
& ".\venv\Scripts\Activate"

# Step 5: Install required dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install flask requests python-dotenv

# Step 6: Create the Flask app file
Write-Host "Creating app.py..." -ForegroundColor Cyan
@"
from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_temperature(query):
    params = {
        "appid": API_KEY,
        "units": "metric"
    }

    if isinstance(query, tuple):
        params.update({"lat": query[0], "lon": query[1]})
    else:
        params.update({"q": query})

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"]
    else:
        return None

@app.route("/temperature", methods=["GET"])
def fetch_temperature():
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
"@ | Out-File -Encoding utf8 "app.py"

# Step 7: Create the .env file
Write-Host "Creating .env file..." -ForegroundColor Cyan
@"
OPENWEATHER_API_KEY=your_api_key_here
"@ | Out-File -Encoding utf8 $envFile

Write-Host "Setup complete! Don't forget to add your OpenWeather API key in .env." -ForegroundColor Green
Write-Host "Run 'python app.py' to start the server." -ForegroundColor Yellow
