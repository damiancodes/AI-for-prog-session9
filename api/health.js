/** Vercel serverless — GET /api/health */

module.exports = function handler(_req, res) {
  res.status(200).json({
    status: "ok",
    key_configured: Boolean(process.env.OPENWEATHER_API_KEY),
  });
};
