const express = require("express");
const Meter = require("../models/Meter");
const auth = require("../middleware/auth");

const router = express.Router();

// All meter routes require authentication
router.use(auth);

// ─── GET /api/meters — list all meters for company ──────
router.get("/", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).sort({
      createdAt: -1,
    });
    res.json({ success: true, count: meters.length, data: meters });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── GET /api/meters/:id — single meter ─────────────────
router.get("/:id", async (req, res) => {
  try {
    const meter = await Meter.findOne({
      _id: req.params.id,
      company: req.company.id,
    });

    if (!meter) {
      return res
        .status(404)
        .json({ success: false, message: "Meter not found" });
    }

    res.json({ success: true, data: meter });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── POST /api/meters — create meter ────────────────────
router.post("/", async (req, res) => {
  try {
    const { location, consumerType, baselineConsumption } = req.body;

    const meter = await Meter.create({
      company: req.company.id,
      location,
      consumerType,
      baselineConsumption,
    });

    res.status(201).json({ success: true, data: meter });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── PUT /api/meters/:id — update meter ─────────────────
router.put("/:id", async (req, res) => {
  try {
    const meter = await Meter.findOneAndUpdate(
      { _id: req.params.id, company: req.company.id },
      req.body,
      { new: true, runValidators: true }
    );

    if (!meter) {
      return res
        .status(404)
        .json({ success: false, message: "Meter not found" });
    }

    res.json({ success: true, data: meter });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── DELETE /api/meters/:id — delete meter ──────────────
router.delete("/:id", async (req, res) => {
  try {
    const meter = await Meter.findOneAndDelete({
      _id: req.params.id,
      company: req.company.id,
    });

    if (!meter) {
      return res
        .status(404)
        .json({ success: false, message: "Meter not found" });
    }

    res.json({ success: true, message: "Meter deleted" });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
