const express = require("express");
const jwt = require("jsonwebtoken");
const Company = require("../models/Company");

const router = express.Router();

const signToken = (company) =>
  jwt.sign(
    { id: company._id, name: company.name },
    process.env.JWT_SECRET || "fallback-secret",
    { expiresIn: process.env.JWT_EXPIRES_IN || "7d" }
  );

// ─── POST /api/auth/register ────────────────────────────
router.post("/register", async (req, res) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({
        success: false,
        message: "name, email, and password are required",
      });
    }

    const exists = await Company.findOne({ email });
    if (exists) {
      return res.status(409).json({
        success: false,
        message: "A company with this email already exists",
      });
    }

    const company = await Company.create({ name, email, password });
    const token = signToken(company);

    res.status(201).json({
      success: true,
      token,
      company: { id: company._id, name: company.name, email: company.email },
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── POST /api/auth/login ───────────────────────────────
router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res
        .status(400)
        .json({ success: false, message: "email and password are required" });
    }

    const company = await Company.findOne({ email }).select("+password");
    if (!company) {
      return res
        .status(401)
        .json({ success: false, message: "Invalid credentials" });
    }

    const isMatch = await company.comparePassword(password);
    if (!isMatch) {
      return res
        .status(401)
        .json({ success: false, message: "Invalid credentials" });
    }

    const token = signToken(company);

    res.json({
      success: true,
      token,
      company: { id: company._id, name: company.name, email: company.email },
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
