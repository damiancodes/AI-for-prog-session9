# APHRC Session 9 — Exercise 4: Weather API Demo

Demo project for **AI for Programming & Development Work** (Exercise 4).  
Build a small OpenWeather client with AI, run it safely with env vars, then explore unit and API tests.

> **Not an automation exercise** — this repo is for **API integration + testing**. Automation is covered separately in the session.

---

## What’s in this repo

| File | Purpose |
|------|---------|
| `weather_solution.py` | Main app — fetch weather, build summaries, optional HTML export |
| `serve_weather.py` | Local server + `index.html` dashboard (3 cities) |
| `api/weather.js` | Vercel serverless API (Node — `/api/weather`) |
| `public/index.html` | Hosted dashboard (Vercel) |
| `vercel.json` | Vercel config for hosted demo link |
| `index.html` | Frontend that calls `/api/weather` |
| `test_weather.py` | Unit, API (mocked), integration, and optional live tests |
| `.env.example` | Template for your API key — copy to `.env` |
| `EXERCISE_4_TASK.md` | Participant task (markdown) |
| `EXERCISE_4_TASK.docx` | Same task — **Word doc for participants** |
| `requirements.txt` | Python dependencies |

---

## Quick start

```bash
git clone <your-repo-url>
cd "AI for programming"

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — add OPENWEATHER_API_KEY (from facilitator chat, not from AI)
```

### Run the app

```bash
# Terminal — all three cities
python weather_solution.py

# Static HTML file
python weather_solution.py --html
open weather.html

# Live dashboard (browser)
python serve_weather.py
# → http://localhost:8765
```

### Deploy to Vercel (share a link in the session)

Good for showing the **3-city dashboard** to remote participants — one URL in chat.

1. Push this repo to GitHub  
2. Import project at [vercel.com](https://vercel.com) → connect the repo  
3. **Settings → Environment Variables** → add `OPENWEATHER_API_KEY` (your key)  
4. **Redeploy** after saving the env var  
5. Share `https://your-project.vercel.app`

**Test:** `/api/health` should return `"key_configured": true`  
**Dashboard:** `/` shows Nairobi, Kampala, Johannesburg

Vercel uses **Node.js** (`api/weather.js`) + static `public/index.html`.  
Python files are local-only (`.vercelignore` excludes them from deploy).

The API key stays on Vercel (server-side) — not in the HTML.

---

### Run tests

```bash
# Fast — no network (recommended in session)
pytest test_weather.py -v

# Optional — one real OpenWeather call
RUN_LIVE_API=1 pytest test_weather.py -v -m integration
```

---

## Security

- **Never** commit `.env` or paste API keys into AI chat, slides, or docs.
- Use `os.getenv("OPENWEATHER_API_KEY")` only.
- Rotate shared training keys after the session.

---

## Unit tests (for slides / demo)

Two functions are covered by **unit tests** (fake data, no network):

| Function | What it does |
|----------|----------------|
| `weather_summary()` | Maps OpenWeather JSON → small dict (city, temp, humidity, …) |
| `_city_card_html()` | Builds one HTML weather card string |

See `test_weather.py` for API (mocked) and integration tests too.

---

## Session flow

1. **Part A — API integration:** Use AI to build the weather script (see `EXERCISE_4_TASK.md`).
2. **Part B — Testing:** Use AI to add or review tests; run `pytest`.
3. **Optional demo:** `serve_weather.py` or `--html` for a visual result.

---

## APHRC · AI Training Series · Session 9

Exercise 4 — API integration & testing (not automation).
