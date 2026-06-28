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

export default async function handler() {
  const key = process.env.OPENWEATHER_API_KEY;
  if (!key) {
    return Response.json(
      {
        error:
          "OPENWEATHER_API_KEY not set. Vercel → Settings → Environment Variables → redeploy.",
      },
      { status: 500 }
    );
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
        return Response.json({ error: "Invalid API key (401)." }, { status: 500 });
      }
      if (!response.ok) {
        return Response.json(
          { error: "OpenWeather error " + response.status + " for " + city },
          { status: 500 }
        );
      }
      results.push(summary(await response.json()));
    }
    return Response.json(results);
  } catch (err) {
    return Response.json(
      { error: err.message || "Weather fetch failed" },
      { status: 500 }
    );
  }
}
