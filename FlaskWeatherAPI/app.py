from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "http://www.7timer.info/bin/api.pl"

def get_temperature(lat, lon):
    """Fetch temperature data from 7Timer! API"""
    params = {
        "lon": lon,
        "lat": lat,
        "product": "civil", 
        "output": "json"
    }

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if "dataseries" in data and len(data["dataseries"]) > 0:
            temp = data["dataseries"][0]["temp2m"] 
            return temp
    return None

@app.route("/temperature", methods=["GET"])
def fetch_temperature():
    """API endpoint to get temperature by lat/lon"""
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if not lat or not lng:
        return jsonify({"error": "Provide lat and lng"}), 400

    temp = get_temperature(lat, lng)

    if temp is not None:
        return jsonify({"temperature": f"{temp}°C"})
    else:
        return jsonify({"error": "Location not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
