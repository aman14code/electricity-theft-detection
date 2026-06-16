/**
 * Seed script — populates the database with realistic demo data.
 *
 * Creates:
 *  - 1 demo company (admin@powerguard.io / password123)
 *  - 8 smart meters across residential & commercial sites
 *  - 30 days of hourly readings with realistic daily patterns
 *  - Injects anomalous data into 2 meters for theft-detection testing
 *
 * Usage:  node src/utils/seedData.js
 */

require("dotenv").config();
const mongoose = require("mongoose");
const Company = require("../models/Company");
const Meter = require("../models/Meter");
const Reading = require("../models/Reading");
const Alert = require("../models/Alert");

const MONGO_URI =
  process.env.MONGO_URI || "mongodb://localhost:27017/theft_detection";

const METERS = [
  { location: "Block A — Residential Tower 1", consumerType: "residential", baselineConsumption: 2.5 },
  { location: "Block B — Residential Tower 2", consumerType: "residential", baselineConsumption: 3.0 },
  { location: "Block C — Residential Villa Zone", consumerType: "residential", baselineConsumption: 4.0 },
  { location: "Market Square — Shop Row 1", consumerType: "commercial", baselineConsumption: 8.0 },
  { location: "Industrial Park — Unit 14", consumerType: "commercial", baselineConsumption: 15.0 },
  { location: "Tech Hub — Office Floor 3", consumerType: "commercial", baselineConsumption: 10.0 },
  { location: "Sunset Colony — House 42 ⚠️ SUSPICIOUS", consumerType: "residential", baselineConsumption: 3.5 },
  { location: "Old Factory Road — Unit 7 ⚠️ SUSPICIOUS", consumerType: "commercial", baselineConsumption: 12.0 },
];

// Realistic daily consumption pattern multipliers (24 hours)
// Index 0 = midnight, index 12 = noon
const RESIDENTIAL_PATTERN = [
  0.3, 0.2, 0.15, 0.15, 0.2, 0.3, 0.6, 0.9,
  1.0, 0.8, 0.6, 0.5, 0.5, 0.4, 0.4, 0.5,
  0.7, 0.9, 1.2, 1.3, 1.2, 1.0, 0.7, 0.4,
];

const COMMERCIAL_PATTERN = [
  0.1, 0.1, 0.1, 0.1, 0.1, 0.15, 0.3, 0.7,
  1.0, 1.2, 1.3, 1.3, 1.1, 1.2, 1.3, 1.2,
  1.1, 1.0, 0.6, 0.3, 0.15, 0.1, 0.1, 0.1,
];

function randomInRange(base, variance) {
  return base + (Math.random() * 2 - 1) * variance;
}

function generateNormalReading(hour, baseline, isResidential) {
  const pattern = isResidential ? RESIDENTIAL_PATTERN : COMMERCIAL_PATTERN;
  const multiplier = pattern[hour];

  return {
    consumptionKwh: Math.max(0, randomInRange(baseline * multiplier, baseline * 0.15)),
    voltage: randomInRange(230, 8),           // 222–238V normal range
    current: Math.max(0.1, randomInRange(baseline * multiplier * 4.3, 1.5)),
    powerFactor: Math.min(1, Math.max(0.7, randomInRange(0.92, 0.06))),
    frequency: randomInRange(50, 0.2),        // 49.8–50.2 Hz
    tamperFlag: false,
  };
}

function generateAnomalousReading(hour, baseline, anomalyType) {
  // Create readings that trigger different detection measures
  switch (anomalyType) {
    case "zero_peak":
      // Consumption drops to 0 during peak hours
      if (hour >= 8 && hour <= 20) {
        return {
          consumptionKwh: 0,
          voltage: randomInRange(230, 5),
          current: 0.01,
          powerFactor: 0.1,
          frequency: randomInRange(50, 0.3),
          tamperFlag: false,
        };
      }
      return generateNormalReading(hour, baseline, false);

    case "voltage_tamper":
      // Abnormal voltage + tamper flag
      return {
        consumptionKwh: Math.max(0, randomInRange(baseline * 0.2, 0.5)),
        voltage: randomInRange(170, 15),        // Very low voltage
        current: randomInRange(0.05, 0.02),     // Near-zero current
        powerFactor: randomInRange(0.3, 0.1),   // Terrible power factor
        frequency: randomInRange(49.0, 0.8),    // Frequency drift
        tamperFlag: Math.random() > 0.4,        // 60% chance tamper flag
      };

    case "flatline":
      // Constant suspiciously identical readings
      return {
        consumptionKwh: 1.0,                    // Always exactly 1.0
        voltage: 230.0,                          // Always exactly 230
        current: 4.35,
        powerFactor: 0.95,
        frequency: 50.0,
        tamperFlag: false,
      };

    default:
      return generateNormalReading(hour, baseline, true);
  }
}

async function seed() {
  console.log("🌱 Connecting to MongoDB…");
  await mongoose.connect(MONGO_URI);

  // Clear existing data
  console.log("🗑️  Clearing existing data…");
  await Promise.all([
    Company.deleteMany({}),
    Meter.deleteMany({}),
    Reading.deleteMany({}),
    Alert.deleteMany({}),
  ]);

  // Create demo company
  console.log("🏢 Creating demo company…");
  const company = await Company.create({
    name: "PowerGuard Utilities",
    email: "admin@powerguard.io",
    password: "password123",
  });

  // Create meters
  console.log("📊 Creating 8 smart meters…");
  const meters = await Meter.insertMany(
    METERS.map((m) => ({ ...m, company: company._id }))
  );

  // Generate 30 days of hourly readings
  const now = new Date();
  const DAYS = 30;
  const totalReadings = [];

  console.log(`⚡ Generating ${DAYS} days × 24 hours × ${meters.length} meters = ${DAYS * 24 * meters.length} readings…`);

  for (let day = DAYS; day >= 0; day--) {
    for (let hour = 0; hour < 24; hour++) {
      const timestamp = new Date(now);
      timestamp.setDate(timestamp.getDate() - day);
      timestamp.setHours(hour, 0, 0, 0);

      for (let i = 0; i < meters.length; i++) {
        const meter = meters[i];
        const isResidential = meter.consumerType === "residential";
        let reading;

        // Inject anomalies into the last 2 meters (suspicious ones)
        if (i === 6 && day <= 10) {
          // Meter 7: zero consumption during peak hours for last 10 days
          reading = generateAnomalousReading(hour, meter.baselineConsumption, "zero_peak");
        } else if (i === 7 && day <= 7) {
          // Meter 8: voltage tampering + tamper flags for last 7 days
          reading = generateAnomalousReading(hour, meter.baselineConsumption, "voltage_tamper");
        } else {
          reading = generateNormalReading(hour, meter.baselineConsumption, isResidential);
        }

        totalReadings.push({
          meter: meter._id,
          timestamp,
          ...reading,
        });
      }
    }
  }

  // Bulk insert in batches of 5000
  console.log(`💾 Inserting ${totalReadings.length} readings…`);
  const BATCH_SIZE = 5000;
  for (let i = 0; i < totalReadings.length; i += BATCH_SIZE) {
    await Reading.insertMany(totalReadings.slice(i, i + BATCH_SIZE), {
      ordered: false,
    });
    process.stdout.write(
      `   Batch ${Math.ceil(i / BATCH_SIZE) + 1}/${Math.ceil(totalReadings.length / BATCH_SIZE)} ✓\n`
    );
  }

  console.log("\n✅ Seed complete!");
  console.log("────────────────────────────────────────────");
  console.log(`   Company: ${company.name}`);
  console.log(`   Login:   admin@powerguard.io / password123`);
  console.log(`   Meters:  ${meters.length}`);
  console.log(`   Readings: ${totalReadings.length}`);
  console.log(`   Suspicious meters: #7 (zero-peak), #8 (voltage-tamper)`);
  console.log("────────────────────────────────────────────");

  await mongoose.disconnect();
  process.exit(0);
}

seed().catch((err) => {
  console.error("❌ Seed failed:", err);
  process.exit(1);
});
