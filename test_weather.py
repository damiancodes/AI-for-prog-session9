"""
Exercise 4 — Weather API test suite (for training demos)

Run all fast tests (no network):
    pytest test_weather.py -v

Run including one live OpenWeather call (needs .env key):
    RUN_LIVE_API=1 pytest test_weather.py -v -m integration

Use this file when explaining test types on slides:
  • UNIT        → weather_summary(), HTML helpers — fake data, no HTTP
  • API (mock)  → fetch_weather() — pretend to be OpenWeather, check status handling
  • INTEGRATION → fetch_all_cities() — several pieces working together
  • LIVE API    → optional real call (slow, uses quota) — marked @integration
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

import weather_solution as ws


# Sample JSON shaped like OpenWeather "current weather" responses
SAMPLE_NAIROBI_RESPONSE = {
    "name": "Nairobi",
    "main": {"temp": 22.4, "feels_like": 21.8, "humidity": 41},
    "weather": [{"description": "overcast clouds"}],
}


# ---------------------------------------------------------------------------
# UNIT TESTS
# One function in isolation. No network, no files, no database.
# AI is good at generating many of these from a function signature.
# ---------------------------------------------------------------------------
class TestWeatherSummaryUnit:
    """UNIT: weather_summary turns raw API JSON into a small dict we use in the app."""

    def test_maps_openweather_fields_to_summary(self):
        """Happy path — every field we display should appear in the summary."""
        result = ws.weather_summary(SAMPLE_NAIROBI_RESPONSE)

        assert result["city"] == "Nairobi"
        assert result["temp"] == 22.4
        assert result["feels_like"] == 21.8
        assert result["humidity"] == 41
        assert result["description"] == "overcast clouds"

    def test_summary_has_exactly_five_keys(self):
        """Contract test — frontend and HTML expect this fixed shape."""
        result = ws.weather_summary(SAMPLE_NAIROBI_RESPONSE)
        assert set(result.keys()) == {"city", "temp", "feels_like", "humidity", "description"}


class TestCityCardHtmlUnit:
    """UNIT: HTML snippet builder — string in, string out."""

    def test_card_contains_city_name_and_rounded_temperature(self):
        """UI test at unit level — we check the rendered string, not a browser."""
        summary = ws.weather_summary(SAMPLE_NAIROBI_RESPONSE)
        html = ws._city_card_html(summary)

        assert "Nairobi" in html
        assert "22°C" in html
        assert "overcast clouds" in html
        assert "Humidity" in html


# ---------------------------------------------------------------------------
# API TESTS (mocked HTTP)
# Test how OUR code talks to an API — without calling OpenWeather for real.
# Mock = fake response we control. Fast, free, works offline.
# ---------------------------------------------------------------------------
class TestFetchWeatherApiMocked:
    """API (mocked): fetch_weather handles HTTP status codes and JSON parsing."""

    @patch("weather_solution.API_KEY", "test-key-not-real")
    @patch("weather_solution.requests.get")
    def test_success_returns_parsed_json(self, mock_get):
        """200 OK — we get back the same JSON OpenWeather would send."""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: SAMPLE_NAIROBI_RESPONSE,
            raise_for_status=lambda: None,
        )

        data = ws.fetch_weather("Nairobi")

        assert data["name"] == "Nairobi"
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args
        assert call_kwargs.kwargs["params"]["q"] == "Nairobi"
        assert call_kwargs.kwargs["params"]["appid"] == "test-key-not-real"
        assert call_kwargs.kwargs["params"]["units"] == "metric"

    @patch("weather_solution.API_KEY", "bad-key")
    @patch("weather_solution.requests.get")
    def test_401_invalid_api_key_raises_clear_error(self, mock_get):
        """401 — wrong key should fail fast with a message humans understand."""
        mock_get.return_value = MagicMock(status_code=401)

        with pytest.raises(RuntimeError, match="Invalid API key"):
            ws.fetch_weather("Nairobi")

    @patch("weather_solution.API_KEY", "test-key")
    @patch("weather_solution.requests.get")
    def test_404_unknown_city_raises_clear_error(self, mock_get):
        """404 — typo in city name should not crash with a generic error."""
        mock_get.return_value = MagicMock(status_code=404)

        with pytest.raises(RuntimeError, match="City not found"):
            ws.fetch_weather("NotARealCityXYZ")

    @patch("weather_solution.API_KEY", None)
    def test_missing_env_key_raises_before_any_http_call(self):
        """Security check — no key means we stop before hitting the network."""
        with pytest.raises(RuntimeError, match="OPENWEATHER_API_KEY"):
            ws.fetch_weather("Nairobi")


# ---------------------------------------------------------------------------
# INTEGRATION TESTS (mocked end-to-end)
# Multiple parts wired together: fetch → parse → list of summaries.
# Still mocked so the test is fast and does not need Wi‑Fi.
# ---------------------------------------------------------------------------
class TestFetchAllCitiesIntegration:
    """INTEGRATION: fetch_all_cities loops cities and returns a list of summaries."""

    @patch("weather_solution.fetch_weather")
    def test_returns_one_summary_per_city(self, mock_fetch):
        """Three cities in → three summaries out (order preserved)."""
        mock_fetch.side_effect = [
            {"name": "Nairobi", "main": {"temp": 20, "feels_like": 19, "humidity": 50}, "weather": [{"description": "cloudy"}]},
            {"name": "Kampala", "main": {"temp": 26, "feels_like": 26, "humidity": 40}, "weather": [{"description": "rain"}]},
            {"name": "Johannesburg", "main": {"temp": 16, "feels_like": 15, "humidity": 70}, "weather": [{"description": "clear"}]},
        ]

        results = ws.fetch_all_cities(["Nairobi", "Kampala", "Johannesburg"])

        assert len(results) == 3
        assert results[0]["city"] == "Nairobi"
        assert results[1]["city"] == "Kampala"
        assert results[2]["city"] == "Johannesburg"
        assert mock_fetch.call_count == 3


# ---------------------------------------------------------------------------
# LIVE API TEST (optional — real network)
# Hits OpenWeather for real. Slower, uses API quota, needs .env key.
# Skip in normal runs; enable for demo: RUN_LIVE_API=1 pytest -m integration
# ---------------------------------------------------------------------------
@pytest.mark.integration
class TestLiveOpenWeatherApi:
    """LIVE API: one real call to OpenWeather — closest to production behaviour."""

    @pytest.mark.skipif(
        not __import__("os").getenv("RUN_LIVE_API"),
        reason="Set RUN_LIVE_API=1 to run live API tests (uses network + quota)",
    )
    def test_nairobi_live_response_has_required_fields(self):
        """Real integration — proves our key, endpoint, and JSON paths all work."""
        if not ws.API_KEY:
            pytest.skip("OPENWEATHER_API_KEY not set in .env")

        data = ws.fetch_weather("Nairobi")
        summary = ws.weather_summary(data)

        assert summary["city"]
        assert isinstance(summary["temp"], (int, float))
        assert summary["description"]
