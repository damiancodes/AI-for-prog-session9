"""Vercel entrypoint — FastAPI app with /api/weather route."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Import weather logic from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from weather_solution import fetch_all_cities

app = FastAPI(title="APHRC Weather Demo")


@app.get("/api/weather")
def get_weather():
    try:
        return fetch_all_cities()
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
