const express = require("express");
const Reading = require("../models/Reading");
const Meter = require("../models/Meter");
const auth = require("../middleware/auth");

const router = express.Router();

router.use(auth);

// ─── POST /api/readings — bulk insert readings ─────────
router.post("/", async (req, res) => {
  try {
    const { readings } = req.body;

    if (!Array.isArray(readings) || readings.length === 0) {
      return res.status(400).json({
        success: false,
        message: "readings array is required and must not be empty",
      });
    }

    // Verify all meters belong to this company
    const meterIds = [...new Set(readings.map((r) => r.meter))];
    const ownedMeters = await Meter.find({
      _id: { $in: meterIds },
      company: req.company.id,
    }).select("_id");

    const ownedIds = new Set(ownedMeters.map((m) => m._id.toString()));
    const filtered = readings.filter((r) => ownedIds.has(r.meter));

    if (filtered.length === 0) {
      return res.status(403).json({
        success: false,
        message: "No readings matched your meters",
      });
    }

    const inserted = await Reading.insertMany(filtered, { ordered: false });

    res.status(201).json({
      success: true,
      count: inserted.length,
      message: `${inserted.length} readings inserted`,
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── GET /api/readings/:meterId — get readings for meter
router.get("/:meterId", async (req, res) => {
  try {
    // Ensure meter belongs to company
    const meter = await Meter.findOne({
      _id: req.params.meterId,
      company: req.company.id,
    });

    if (!meter) {
      return res
        .status(404)
        .json({ success: false, message: "Meter not found" });
    }

    const days = parseInt(req.query.days) || 7;
    const since = new Date();
    since.setDate(since.getDate() - days);

    const readings = await Reading.find({
      meter: req.params.meterId,
      timestamp: { $gte: since },
    }).sort({ timestamp: 1 });

    res.json({ success: true, count: readings.length, data: readings });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
