/** Vercel serverless — GET /api/health (check env var is configured) */

module.exports = (req, res) => {
  res.status(200).json({
    status: "ok",
    key_configured: Boolean(process.env.OPENWEATHER_API_KEY),
  });
};
