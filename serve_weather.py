"""Tiny local server: HTML frontend + /api/weather (key stays in .env)."""

import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from weather_solution import fetch_all_cities

ROOT = Path(__file__).resolve().parent
PORT = 8765


class WeatherHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/weather":
            self._send_json_weather()
            return

        if path in ("/", ""):
            self.path = "/index.html"

        super().do_GET()

    def _send_json_weather(self):
        try:
            payload = fetch_all_cities()
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[server] {args[0]}")


def main():
    url = f"http://localhost:{PORT}"
    server = HTTPServer(("localhost", PORT), WeatherHandler)
    print(f"Serving {url}  (Ctrl+C to stop)")
    print("API key loaded from .env — not exposed to the browser.")
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
