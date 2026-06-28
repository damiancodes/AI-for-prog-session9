/** GET /api/health — check env var is set on Vercel */

module.exports = function handler(_req, res) {
  res.status(200).json({
    status: "ok",
    key_configured: Boolean(process.env.OPENWEATHER_API_KEY),
  });
};
