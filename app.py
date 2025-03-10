from flask import Flask, request, jsonify
import requests
import psycopg2
from psycopg2 import sql
from datetime import date
from psycopg2.extras import RealDictCursor


app = Flask(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DB_CONFIG = {
    "dbname": "playground",
    "user": "player",
    "password": "iAMready",
    "host": "dev-common-eksom-vend-db.c3ucia680nmx.af-south-1.rds.amazonaws.com",
    "port": 5432
}

def log_forecast(lat, lng, temperature, forecast_date=None):
    """Logs a temperature forecast into the database, preventing duplicates."""
    if forecast_date is None:
        forecast_date = date.today()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        query = sql.SQL("""
            INSERT INTO weather_forecast(latitude, longitude, forecast_date, temperature)
            VALUES (%s, %s, %s, %s);
        """)
        
        cur.execute(query, (lat, lng, forecast_date, temperature))
        conn.commit()
        
        print(f"✅ Logged forecast: lat={lat}, lng={lng}, date={forecast_date}, temp={temperature}°C")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    """Fetches temperature logs from PostgreSQL based on a date range."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "Missing start_date or end_date"}), 400

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, latitude, longitude, forecast_date, temperature
            FROM weather_forecast
            WHERE forecast_date BETWEEN %s AND %s
            ORDER BY forecast_date ASC;
        """

        cur.execute(query, (start_date, end_date))
        records = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(records)

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/forecast", methods=["GET"])
def forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing lat or lon parameters"}), 400

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m",
                "timezone": "auto"
            },
            timeout=5
        )
        data = response.json()

        if "current" not in data or "temperature_2m" not in data["current"]:
            return jsonify({"error": "Invalid response from weather API"}), 500

        log_forecast(lat, lon, data["current"]["temperature_2m"])

        return jsonify({
            "latitude": lat,
            "longitude": lon,
            "temperature_celsius": data["current"]["temperature_2m"]
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


# test command:
# http://localhost:5000/logs?start_date=2025-03-01&end_date=2025-03-10
