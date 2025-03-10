from flask import Flask, request, jsonify
import requests
import psycopg2
import redis
from datetime import date, timedelta
from psycopg2.extras import RealDictCursor
import json

app = Flask(__name__)

# Redis configuration
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

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

        # Check if the record already exists
        check_query = """
            SELECT 1 FROM weather_forecast
            WHERE latitude = %s AND longitude = %s AND forecast_date = %s;
        """
        cur.execute(check_query, (lat, lng, forecast_date))
        existing_record = cur.fetchone()

        if existing_record:
            response = {"message": "Forecast already logged", "latitude": lat, "longitude": lng, "date": str(forecast_date)}
        else:
            query = """
                INSERT INTO weather_forecast(latitude, longitude, forecast_date, temperature)
                VALUES (%s, %s, %s, %s);
            """
            cur.execute(query, (lat, lng, forecast_date, temperature))
            conn.commit()
            response = {"message": "Forecast logged successfully", "latitude": lat, "longitude": lng, "date": str(forecast_date), "temperature": temperature}

        cur.close()
        conn.close()
        return response
    except Exception as e:
        return {"error": str(e)}

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

    cache_key = f"forecast:{lat}:{lon}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return jsonify(json.loads(cached_data))

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

        forecast_response = log_forecast(lat, lon, data["current"]["temperature_2m"])
        redis_client.setex(cache_key, 600, json.dumps(forecast_response))  # Cache for 10 minutes

        return jsonify(forecast_response)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# test command:
# http://localhost:5000/logs?start_date=2025-03-01&end_date=2025-03-10
