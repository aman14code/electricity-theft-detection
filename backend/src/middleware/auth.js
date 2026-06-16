const jwt = require("jsonwebtoken");

/**
 * JWT authentication middleware.
 * Expects header: Authorization: Bearer <token>
 * Attaches decoded payload to req.company = { id, name }
 */
const auth = (req, res, next) => {
  const header = req.header("Authorization");

  if (!header || !header.startsWith("Bearer ")) {
    return res.status(401).json({
      success: false,
      message: "Access denied — no token provided",
    });
  }

  const token = header.split(" ")[1];

  try {
    const decoded = jwt.verify(
      token,
      process.env.JWT_SECRET || "fallback-secret"
    );
    req.company = { id: decoded.id, name: decoded.name };
    next();
  } catch (err) {
    return res.status(401).json({
      success: false,
      message: "Invalid or expired token",
    });
  }
};

module.exports = auth;
