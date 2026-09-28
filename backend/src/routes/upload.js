const express = require("express");
const router = express.Router();
const multer = require("multer");
const csv = require("csv-parser");
const fs = require("fs");
const path = require("path");
const Meter = require("../models/Meter");
const Reading = require("../models/Reading");
const auth = require("../middleware/auth");

const upload = multer({ dest: "uploads/" });

/**
 * @route   POST /api/upload/csv
 * @desc    Upload a CSV of meters and readings for automated ingestion
 * @access  Private
 */
router.post("/csv", auth, upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ success: false, error: "Please upload a CSV file" });
  }

  const results = [];
  
  // Parse CSV
  fs.createReadStream(req.file.path)
    .pipe(csv())
    .on("data", (data) => results.push(data))
    .on("end", async () => {
      try {
        let newMetersCount = 0;
        let newReadingsCount = 0;

        for (const row of results) {
          // Expected CSV Headers: meterId, consumerName, areaCode, substation, timestamp, kwh, voltage, current
          const { meterId, consumerName, areaCode, substation, timestamp, kwh, voltage, current } = row;

          if (!meterId || !kwh || !timestamp) continue;

          // 1. Find or create meter
          let meter = await Meter.findOne({ location: meterId, company: req.user.id });
          
          if (!meter) {
            meter = await Meter.create({
              company: req.user.id,
              location: meterId,
              consumerName: consumerName || "Unknown",
              areaCode: areaCode || "General",
              substation: substation || "Main Substation",
              consumerType: "residential",
              baselineConsumption: 1.5,
            });
            newMetersCount++;
          }

          // 2. Add reading
          await Reading.create({
            meter: meter._id,
            timestamp: new Date(timestamp),
            consumptionKwh: parseFloat(kwh),
            voltage: voltage ? parseFloat(voltage) : 230,
            current: current ? parseFloat(current) : 5,
            powerFactor: 0.95,
            frequency: 50,
          });
          newReadingsCount++;
        }

        // Clean up file
        fs.unlinkSync(req.file.path);

        res.json({
          success: true,
          message: "Batch upload successful",
          data: {
            metersCreated: newMetersCount,
            readingsAdded: newReadingsCount
          }
        });

      } catch (err) {
        console.error("Bulk Upload Error:", err);
        fs.unlinkSync(req.file.path);
        res.status(500).json({ success: false, error: "Failed to process bulk upload" });
      }
    });
});

module.exports = router;
