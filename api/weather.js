/** Vercel serverless — GET /api/weather */

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

module.exports = async function handler(_req, res) {
  const key = process.env.OPENWEATHER_API_KEY;
  if (!key) {
    res.status(500).json({
      error:
        "OPENWEATHER_API_KEY not set. Vercel → Settings → Environment Variables → redeploy.",
    });
    return;
  }

  try {
    const results = [];
    for (const city of CITIES) {
      const url =
        BASE +
        "?q=" +
        encodeURIComponent(city) +
        "&appid=" +
        encodeURIComponent(key) +
        "&units=metric";
      const response = await fetch(url);
      if (response.status === 401) {
        res.status(500).json({ error: "Invalid API key (401)." });
        return;
      }
      if (!response.ok) {
        res.status(500).json({ error: "OpenWeather error " + response.status + " for " + city });
        return;
      }
      results.push(summary(await response.json()));
    }
    res.status(200).json(results);
  } catch (err) {
    res.status(500).json({ error: err.message || "Weather fetch failed" });
  }
};
