export default function handler() {
  return Response.json({
    status: "ok",
    key_configured: Boolean(process.env.OPENWEATHER_API_KEY),
  });
}
