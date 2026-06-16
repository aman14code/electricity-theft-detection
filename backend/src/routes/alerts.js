const express = require("express");
const Alert = require("../models/Alert");
const Meter = require("../models/Meter");
const auth = require("../middleware/auth");

const router = express.Router();

router.use(auth);

// ─── GET /api/alerts — list all alerts for company ──────
router.get("/", async (req, res) => {
  try {
    // Get all meter IDs owned by this company
    const meters = await Meter.find({ company: req.company.id }).select("_id");
    const meterIds = meters.map((m) => m._id);

    const { status } = req.query;
    const filter = { meter: { $in: meterIds } };
    if (status) filter.status = status;

    const alerts = await Alert.find(filter)
      .populate("meter", "location consumerType baselineConsumption")
      .sort({ createdAt: -1 })
      .limit(200);

    res.json({ success: true, count: alerts.length, data: alerts });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── PATCH /api/alerts/:id — update alert status ────────
router.patch("/:id", async (req, res) => {
  try {
    const { status } = req.body;

    if (!["pending", "investigating", "resolved"].includes(status)) {
      return res.status(400).json({
        success: false,
        message: "status must be pending, investigating, or resolved",
      });
    }

    // Verify alert belongs to this company via meter ownership
    const alert = await Alert.findById(req.params.id).populate("meter");
    if (!alert) {
      return res
        .status(404)
        .json({ success: false, message: "Alert not found" });
    }

    const meter = await Meter.findOne({
      _id: alert.meter._id,
      company: req.company.id,
    });

    if (!meter) {
      return res.status(403).json({
        success: false,
        message: "Not authorized to modify this alert",
      });
    }

    alert.status = status;
    await alert.save();

    res.json({ success: true, data: alert });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
