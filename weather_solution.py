"""Reference solution for Exercise 4 — facilitator demo only."""

import os
import random
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
MAX_RETRIES = 3
CITIES = ["Nairobi", "Kampala", "Johannesburg"]


def fetch_weather(city: str) -> dict:
    if not API_KEY:
        raise RuntimeError(
            "Set OPENWEATHER_API_KEY in your environment or .env file"
        )

    params = {"q": city, "appid": API_KEY, "units": "metric"}
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)

            if response.status_code in {429, 500, 502, 503, 504}:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()
                delay = (2**attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue

            if response.status_code == 401:
                raise RuntimeError("Invalid API key (401). Check OPENWEATHER_API_KEY.")
            if response.status_code == 404:
                raise RuntimeError(f"City not found (404): {city}")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            last_error = exc
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Request failed after {MAX_RETRIES} tries") from exc
            delay = (2**attempt) + random.uniform(0, 1)
            time.sleep(delay)

    raise RuntimeError("Unexpected retry loop exit") from last_error


def weather_summary(data: dict) -> dict:
    return {
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
    }


def fetch_all_cities(cities: list[str] | None = None) -> list[dict]:
    cities = cities or CITIES
    return [weather_summary(fetch_weather(city)) for city in cities]


def _city_card_html(w: dict) -> str:
    return f"""
    <div class="card">
      <div class="city">{w["city"]}</div>
      <div class="temp">{round(w["temp"])}°C</div>
      <div class="desc">{w["description"]}</div>
      <div class="meta">
        <div><span>Feels like</span>{round(w["feels_like"])}°C</div>
        <div><span>Humidity</span>{w["humidity"]}%</div>
      </div>
    </div>"""


def write_html(cities_data: list[dict] | None = None, path: str = "weather.html") -> str:
    """Write a standalone HTML file you can double-click to open."""
    cities_data = cities_data or fetch_all_cities()
    cards = "".join(_city_card_html(w) for w in cities_data)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>East &amp; Southern Africa Weather</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      min-height: 100vh;
      background: linear-gradient(160deg, #0f172a, #1e3a5f);
      color: #f8fafc; padding: 2rem 1.5rem;
    }}
    .header {{ text-align: center; margin-bottom: 1.5rem; }}
    .label {{
      font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.75;
    }}
    .grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1rem; max-width: 960px; margin: 0 auto;
    }}
    .card {{
      text-align: center; padding: 1.5rem; border-radius: 16px;
      background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
    }}
    .city {{ font-size: 1.5rem; font-weight: 700; }}
    .temp {{ font-size: 2.75rem; font-weight: 800; margin: 0.5rem 0; }}
    .desc {{ text-transform: capitalize; opacity: 0.9; margin-bottom: 1rem; }}
    .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.9rem; }}
    .meta div {{ background: rgba(0,0,0,0.2); border-radius: 8px; padding: 0.5rem; }}
    .meta span {{ display: block; opacity: 0.7; font-size: 0.75rem; }}
  </style>
</head>
<body>
  <div class="header"><p class="label">Exercise 4 · OpenWeather API</p></div>
  <div class="grid">{cards}</div>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def main() -> None:
    import sys

    for w in fetch_all_cities():
        print(f'{w["city"]} {w["temp"]}°C {w["description"]}')

    if "--html" in sys.argv:
        path = write_html()
        print(f"Wrote {path} — open it in your browser.")


if __name__ == "__main__":
    main()
