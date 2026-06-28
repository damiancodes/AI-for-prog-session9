/** Vercel serverless — GET /api/weather (key from OPENWEATHER_API_KEY env var) */

const CITIES = ["Nairobi", "Kampala", "Johannesburg"];
const BASE = "https://api.openweathermap.org/data/2.5/weather";

function summary(data) {
  return {
    city: data.name,
    temp: data.main.temp,
    feels_like: data.main.feels_like,
    humidity: data.main.humidity,
    description: data.weather[0].description,
  };
}

module.exports = async (req, res) => {
  const key = process.env.OPENWEATHER_API_KEY;
  if (!key) {
    return res.status(500).json({
      error:
        "OPENWEATHER_API_KEY not set. Add it in Vercel → Settings → Environment Variables, then redeploy.",
    });
  }

  try {
    const results = [];
    for (const city of CITIES) {
      const url = `${BASE}?q=${encodeURIComponent(city)}&appid=${key}&units=metric`;
      const response = await fetch(url, { signal: AbortSignal.timeout(10000) });
      if (response.status === 401) {
        return res.status(500).json({ error: "Invalid API key (401). Check OPENWEATHER_API_KEY on Vercel." });
      }
      if (response.status === 404) {
        return res.status(500).json({ error: `City not found (404): ${city}` });
      }
      if (!response.ok) {
        return res.status(500).json({ error: `OpenWeather error ${response.status} for ${city}` });
      }
      results.push(summary(await response.json()));
    }
    return res.status(200).json(results);
  } catch (err) {
    return res.status(500).json({ error: err.message || "Weather fetch failed" });
  }
};
