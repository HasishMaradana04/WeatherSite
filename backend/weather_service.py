from datetime import date
import requests


def geocode_location(location: str):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1, "language": "en", "format": "json"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        raise ValueError("Location not found")
    hit = results[0]
    return {
        "name": hit.get("name"),
        "country": hit.get("country"),
        "latitude": hit.get("latitude"),
        "longitude": hit.get("longitude"),
    }


def get_weather(latitude: float, longitude: float, start_date: str | None = None, end_date: str | None = None):
    today = date.today().isoformat()
    start_date = start_date or today
    end_date = end_date or today

    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "start_date": start_date,
            "end_date": end_date,
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()
