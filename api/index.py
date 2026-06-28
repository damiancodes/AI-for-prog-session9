"""Vercel entrypoint — self-contained FastAPI (no cross-file imports)."""

import os

import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="APHRC Weather Demo")

CITIES = ["Nairobi", "Kampala", "Johannesburg"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def _summary(data: dict) -> dict:
    return {
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
    }


def fetch_all_cities() -> list[dict]:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENWEATHER_API_KEY not set. Add it in Vercel → Settings → Environment Variables."
        )

    results = []
    for city in CITIES:
        response = requests.get(
            BASE_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        if response.status_code == 401:
            raise RuntimeError("Invalid API key (401). Check OPENWEATHER_API_KEY on Vercel.")
        if response.status_code == 404:
            raise RuntimeError(f"City not found (404): {city}")
        response.raise_for_status()
        results.append(_summary(response.json()))
    return results


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "key_configured": bool(os.getenv("OPENWEATHER_API_KEY")),
    }


@app.get("/api/weather")
def get_weather():
    try:
        return fetch_all_cities()
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
