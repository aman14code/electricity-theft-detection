# ⚡ PowerGuard — Electricity Theft Detection System
## Complete Interview & Project Presentation Guide

> This document prepares you to explain your project **deeply** in any interview or presentation using the frameworks: **STAR**, **PREP**, **Problem → Approach → Trade-off**, **Architecture → Flow → Failure**, and **Ownership**.

---

## 📌 Table of Contents

1. [Project Overview (Elevator Pitch)](#1-project-overview--elevator-pitch)
2. [STAR — Tell Your Project Story](#2-star--tell-your-project-story)
3. [PREP — Explain Every Technical Decision](#3-prep--explain-every-technical-decision)
4. [Problem → Approach → Trade-off](#4-problem--approach--trade-off)
5. [Architecture → Flow → Failure](#5-architecture--flow--failure)
6. [Ownership — What YOU Did](#6-ownership--what-you-did)
7. [Deep-Dive: ML Detection Engine](#7-deep-dive-ml-detection-engine)
8. [Deep-Dive: Backend API Design](#8-deep-dive-backend-api-design)
9. [Deep-Dive: Frontend & UX](#9-deep-dive-frontend--ux)
10. [Deep-Dive: DevOps & Deployment](#10-deep-dive-devops--deployment)
11. [Common Interview Questions & Answers](#11-common-interview-questions--answers)
12. [What I Would Change Now](#12-what-i-would-change-now)

---

## 1. Project Overview — Elevator Pitch

> **PowerGuard** is a full-stack, ML-powered platform that detects electricity theft from smart meter telemetry data in real-time. It uses an **8-measure weighted heuristic engine** combined with a **Random Forest classifier** trained on synthetic data to analyze 6-dimensional meter readings (consumption, voltage, current, power factor, frequency, tamper flags) and flag suspicious patterns like meter bypassing, consumption drops during peak hours, and hardware tampering — with per-measure explainability for each prediction.

**Key numbers to remember:**
- 4-service microservice architecture (Frontend + Backend + ML Service + MongoDB)
- 8 independent anomaly detection measures
- 24 engineered features for the ML model (14 core + 10 engineered)
- 7 types of synthetic theft scenarios for model training
- ~7,200 synthetic training samples (3,000 normal + 4,200 anomalous)
- 4 risk levels: Low (<30%), Medium (30–49%), High (50–74%), Critical (≥75%)

---

## 2. STAR — Tell Your Project Story

> **Use when they ask: "Tell me about your project."**

### S — Situation: What problem were you solving?

*"India loses approximately ₹1.5 lakh crore annually to electricity theft, which accounts for roughly 20-25% of total electricity generated. Traditional detection methods rely on manual meter inspections, which are expensive, slow, and easily gamed by sophisticated theft techniques like meter bypassing, voltage manipulation, and data spoofing. Power distribution companies needed a way to detect theft automatically from the smart meter data they were already collecting."*

### T — Task: What were you responsible for?

*"I designed and built a complete end-to-end system — from the ML anomaly detection engine that analyzes 6-dimensional smart meter telemetry, to the Node.js backend API that orchestrates data flow, to the React dashboard that utility operators use to monitor their grid. I was responsible for the architecture decisions, the detection algorithm design, the database schema, the API design, and the deployment pipeline."*

### A — Action: What did you build, decide, or fix?

*"I broke the system into 4 independent services communicating over REST:*
1. *A **React + Vite** dashboard for utility operators to manage meters, view trends, run analysis, and manage alerts*
2. *A **Node.js/Express** API handling authentication, CRUD operations, data aggregation, and orchestrating calls to the ML service*
3. *A **FastAPI Python** microservice running an 8-measure detection engine with optional trained model support*
4. *A **MongoDB** database storing meters, hourly readings, alerts with per-measure breakdowns, and company data*

*The most technically challenging part was designing the detection engine. I created 8 independent anomaly measures — each analyzing a different dimension of theft (consumption drops, current bypass, voltage tampering, power factor manipulation, frequency deviation, hardware tamper flags, pattern irregularity, and flat-line detection). Each measure produces a score between 0 and 1, and they're combined using a weighted average with boosting logic for high-confidence multi-measure agreement.*

*I also built a training pipeline that generates realistic synthetic smart meter data for 7 different theft scenarios and trains a Random Forest classifier with 24 engineered features that exactly match what the production API sends."*

### R — Result: What was the outcome?

*"The system successfully detects all 7 major categories of electricity theft with explainable per-measure breakdowns. The ML model achieves high accuracy on synthetic data with 5-fold cross-validation. The dashboard gives utility operators real-time visibility into their grid with one-click bulk analysis across their entire meter network, and the system auto-creates prioritized alerts with a workflow for investigating and resolving cases. The CSV export feature enables regulatory reporting."*

---

## 3. PREP — Explain Every Technical Decision

> **Use when they ask: "Why did you use X?"**
> P — Point | R — Reason | E — Evidence | P — Connect back to project

---

### "Why React + Vite instead of Next.js?"

| Step | Answer |
|---|---|
| **Point** | I chose React with Vite as the frontend framework |
| **Reason** | This is a single-page dashboard app — operators log in and stay on one session. There's no SEO requirement, no server-side rendering needed, and no public-facing pages. Vite gives instant HMR and sub-second builds, which was important during rapid prototyping of the 7+ pages |
| **Evidence** | Vite's dev server starts in <300ms vs Next.js's 2-3 seconds. The app has zero public routes — everything is behind JWT auth, so SSR adds zero value but doubles deployment complexity |
| **Connect** | For an internal tool used by utility operators, fast development iteration and simple deployment (static files on any CDN) mattered more than SEO or server-side features |

---

### "Why Node.js/Express for the backend instead of Python/Django?"

| Step | Answer |
|---|---|
| **Point** | I used Node.js with Express for the API layer |
| **Reason** | The backend is primarily an orchestration layer — it receives requests, queries MongoDB, computes statistical features, forwards to the ML service, and stores results. Node.js excels at this I/O-bound, async work. It also shares the same JSON format with the frontend, eliminating serialization overhead |
| **Evidence** | The bulk analysis endpoint (`Promise.allSettled`) analyzes all meters concurrently — Node's event loop handles this naturally without threading complexity. Express middleware (CORS, Morgan, JSON parsing, JWT auth) is configured in 5 lines |
| **Connect** | The computationally heavy ML work runs in Python where it belongs. Node.js handles what it's best at: API routing, async I/O, and MongoDB queries |

---

### "Why FastAPI for the ML service?"

| Step | Answer |
|---|---|
| **Point** | I used FastAPI as the ML microservice framework |
| **Reason** | FastAPI gives automatic OpenAPI docs, Pydantic validation (critical for 6-dimensional telemetry data), async support, and native Python integration with scikit-learn/numpy |
| **Evidence** | Pydantic schemas validate every meter reading field (consumption ≥ 0, power_factor 0–1, etc.) before it hits the detection engine. Auto-generated `/docs` endpoint lets me test the API interactively during development |
| **Connect** | Type safety at the ML service boundary catches data quality issues before they corrupt predictions — a malformed reading with negative voltage would be rejected with a clear 422 error |

---

### "Why MongoDB instead of PostgreSQL?"

| Step | Answer |
|---|---|
| **Point** | I chose MongoDB as the database |
| **Reason** | Smart meter readings are time-series data with variable fields. Each reading has 6 telemetry dimensions, and the anomaly breakdown stored in alerts is a nested object with 8 scores. MongoDB's document model stores this naturally without join tables |
| **Evidence** | The `anomalyBreakdown` field in alerts stores 8 scores as a nested document — in PostgreSQL this would need a separate table or JSONB column (losing type safety). Compound indexes on `{meter: 1, timestamp: -1}` give fast range queries for "last 30 days of readings" |
| **Connect** | For this use case, schema flexibility and natural document storage outweigh PostgreSQL's ACID transactions (we don't need multi-document transactions for meter readings) |

---

### "Why a separate ML microservice instead of running detection in Node.js?"

| Step | Answer |
|---|---|
| **Point** | I separated the ML engine into its own FastAPI microservice |
| **Reason** | Three reasons: (1) Python has the ML ecosystem — scikit-learn, numpy, joblib; (2) The ML service can be scaled, deployed, and updated independently; (3) If the ML service goes down, the backend has a built-in JavaScript fallback heuristic that mirrors the same 8-measure logic |
| **Evidence** | The backend's `analyze.js` has a complete `computeFallbackHeuristic()` function (100+ lines) that runs the same 8-measure algorithm in JavaScript — so the system never fails silently. The `try/catch` around the ML service call automatically falls back |
| **Connect** | This gives me zero-downtime resilience. Even during ML model retraining or service updates, the system continues detecting theft using the deterministic fallback |

---

### "Why JWT instead of session-based auth?"

| Step | Answer |
|---|---|
| **Point** | I implemented JWT (JSON Web Tokens) for authentication |
| **Reason** | JWTs are stateless — the backend doesn't need to store session data in MongoDB. The token contains the company ID and name, and is verified on every request via a middleware. This makes the API horizontally scalable |
| **Evidence** | The auth middleware is 15 lines — it extracts the Bearer token, verifies with `jwt.verify()`, and attaches `req.company = { id, name }`. Every protected route can then scope queries to `company: req.company.id` for multi-tenant data isolation |
| **Connect** | For an API serving multiple power distribution companies, stateless auth means any backend instance can serve any request without shared session storage |

---

## 4. Problem → Approach → Trade-off

> **Use for architecture or technology questions**

---

### Problem 1: How to detect electricity theft from raw meter data?

| | Details |
|---|---|
| **Problem** | Raw meter readings are just numbers (kWh, voltage, current). Theft manifests as subtle statistical patterns — not obvious from individual readings |
| **Approaches Considered** | (1) Simple threshold rules (if consumption < X, flag it); (2) Single ML model (Random Forest); (3) Multi-measure heuristic engine; (4) Hybrid: heuristic + ML |
| **What I Chose** | Hybrid approach — 8-measure weighted heuristic with optional ML model overlay |
| **Why** | Threshold rules miss sophisticated theft. A single ML model is a black box — operators won't trust alerts without explainability. The heuristic gives per-measure breakdowns ("tamper detection: 90%, consumption drop: 70%") that operators can understand and act on. The ML model, when available, provides better overall accuracy while still using the heuristic breakdown for explainability |
| **Trade-off** | The heuristic requires manual weight tuning (I set consumption_drop=25%, tamper=20%, etc. based on domain research). An end-to-end ML model would learn weights automatically but lose explainability |

---

### Problem 2: How to handle the ML service being unavailable?

| | Details |
|---|---|
| **Problem** | If the Python ML service crashes, the entire detection pipeline fails |
| **Approaches Considered** | (1) Return an error to the user; (2) Queue the request for later; (3) Built-in fallback heuristic in Node.js |
| **What I Chose** | Triple-layer fallback: ML model → Python heuristic → Node.js fallback heuristic |
| **Why** | The system should always provide a result. Even a heuristic-based estimate is better than "service unavailable." The fallback mirrors the same 8-measure algorithm, so results are consistent |
| **Trade-off** | Maintaining the same algorithm in two languages (Python + JavaScript) creates a code duplication risk — if I update the weights in Python, I must remember to update the JS fallback. I accepted this because availability > DRY principle for critical infrastructure |

---

### Problem 3: No real theft data to train the ML model

| | Details |
|---|---|
| **Problem** | Real electricity theft data is proprietary and unavailable. Can't train a supervised ML model without labeled data |
| **Approaches Considered** | (1) Unsupervised anomaly detection (Isolation Forest, Autoencoders); (2) Generate synthetic data; (3) Use only heuristic rules |
| **What I Chose** | Synthetic data generation with 7 realistic theft scenarios |
| **Why** | I studied published research on electricity theft patterns and modeled 7 distinct scenarios: zero-peak consumption, voltage tampering, current bypass, flat-line spoofing, night-inversion, gradual drop, and partial theft. Each generates realistic hourly readings with proper daily consumption patterns (residential peaks morning/evening, commercial peaks 9-5) |
| **Trade-off** | Synthetic data may not capture all real-world edge cases. The model could overfit to the simulated patterns. But by generating 7 diverse scenarios at different baselines (1.5–20 kWh) with varying durations (7–30 days), I maximized coverage. The heuristic fallback catches cases the model misses |

---

### Problem 4: Multi-tenant data isolation

| | Details |
|---|---|
| **Problem** | Multiple power distribution companies use the same platform. Company A must never see Company B's meters or alerts |
| **Approaches Considered** | (1) Separate databases per company; (2) Row-level filtering via company ID; (3) Separate deployments |
| **What I Chose** | Row-level filtering — every query is scoped with `{ company: req.company.id }` |
| **Why** | Simple, effective, and proven. The JWT token carries the company ID, and every MongoDB query includes it as a filter. Compound indexes like `{company: 1, isActive: 1}` on the Meter collection make this fast |
| **Trade-off** | A single corrupted query that forgets the company filter could leak data. In production, I'd add a Mongoose middleware that auto-injects the company filter on all queries as a safety net |

---

## 5. Architecture → Flow → Failure

> **When they go deeper technically**

---

### Architecture: How do the components communicate?

```
┌─────────────────┐   REST API    ┌─────────────────────┐   HTTP POST    ┌──────────────────┐
│  React Frontend  │ ─────────── ▶ │  Node.js/Express API │ ────────────▶ │  FastAPI ML Svc  │
│  (Vite, Tailwind)│ ◀─────────── │   (Auth, CRUD, Logic) │ ◀──────────── │  (Heuristic + ML) │
│  Port: 5173      │  JSON resp   │   Port: 5000          │  JSON resp    │  Port: 8000       │
└─────────────────┘              └──────────┬──────────┘             └──────────────────┘
                                            │ Mongoose ODM
                                   ┌────────▼────────┐
                                   │   MongoDB 7      │
                                   │   Port: 27017    │
                                   └─────────────────┘
```

**Communication patterns:**
- **Frontend → Backend**: Axios HTTP client with JWT interceptor. Base URL from `VITE_API_URL` env variable. Auto-redirect to `/login` on 401 responses
- **Backend → ML Service**: Axios POST to `ML_SERVICE_URL/predict` with 15-second timeout. Falls back to built-in heuristic on failure
- **Backend → MongoDB**: Mongoose ODM with connection retry logic (5-second intervals) and disconnection handling
- **All services connected via Docker bridge network** (`theft-net`) for container-to-container DNS resolution

---

### Flow: What happens from user action to response?

#### Flow 1: "Analyze Anomalies" button click on a meter

```
User clicks "Analyze Anomalies"
    │
    ▼
Frontend: POST /api/analyze/:meterId
    │ (JWT token attached via Axios interceptor)
    ▼
Backend Auth Middleware: Verify JWT → extract company ID
    │
    ▼
Backend: Verify meter ownership (Meter.findOne({ _id, company }))
    │
    ▼
Backend: Fetch last 30 days of readings
    │ Reading.find({ meter, timestamp: { $gte: 30 days ago } })
    │ Returns up to ~720 hourly readings
    ▼
Backend: Compute statistical features
    │ For each dimension (consumption, voltage, current, PF, frequency):
    │   → Calculate mean, std, min, max
    │ Plus: tamper_ratio, baseline_consumption, consumer_type, reading_count
    ▼
Backend: POST to ML Service (http://ml-service:8000/predict)
    │ Payload: { meter_id, features, readings[] }
    │ Timeout: 15 seconds
    ▼
ML Service: Pydantic validates all 720+ readings
    │ (consumption ≥ 0, voltage ≥ 0, power_factor 0–1, etc.)
    ▼
ML Service: Try trained model first (model.pkl)
    │ If exists → Extract 24 features → RandomForest.predict_proba()
    │ If not   → Fall back to 8-measure heuristic
    ▼
ML Service: 8-Measure Heuristic Engine (or ML + heuristic for breakdown)
    │
    │ 1. Consumption Drop (25%): Zero kWh during peak hours 8-20?
    │ 2. Current Anomaly  (15%): Low current + normal voltage = bypass?
    │ 3. Tamper Detection  (20%): Hardware tamper flags? Consecutive runs?
    │ 4. Voltage Anomaly   (10%): Outside 190-250V safe band?
    │ 5. Power Factor      (10%): Unusually low PF = load manipulation?
    │ 6. Pattern Irregularity(10%): High CV? Day/night inversion?
    │ 7. Frequency Deviation (5%): Outside 49-51 Hz?
    │ 8. Flat-line Detection (5%): Constant readings = spoofed meter?
    │
    │ → Weighted combination → Boosting if 3+ measures > 0.5
    │ → Boosting if any measure ≥ 0.9 (floor at 40%)
    ▼
ML Service returns:
    │ { theft_probability, anomaly_flag, anomaly_breakdown{8 scores},
    │   source, confidence, risk_level }
    ▼
Backend: If anomaly_flag == true
    │ → Create Alert document in MongoDB with breakdown
    │ → Return { anomalyDetected: true, alert, mlResult }
    ▼
Frontend: Display result
    │ → If anomaly: Red banner + 8-measure progress bars
    │ → If clean: Green "All Clear" banner
    │ → Toast notification
```

#### Flow 2: Bulk Analysis (Reports page)

```
User clicks "Analyze All Meters"
    ▼
Frontend: POST /api/analyze/bulk
    ▼
Backend: Fetch ALL meters for company
    ▼
Backend: Promise.allSettled() → analyze each meter IN PARALLEL
    │ For each meter:
    │   1. Fetch readings (last 30 days)
    │   2. Compute features
    │   3. POST to ML service
    │   4. If anomaly → Create Alert
    ▼
Backend returns:
    │ { summary: { total, analyzed, anomalies }, results[] }
    ▼
Frontend: Bar chart sorted by risk + Per-meter scorecard table
    │ Optional: CSV export
```

---

### Failure: What happens when something breaks?

| Failure Scenario | What Happens | Recovery Mechanism |
|---|---|---|
| **ML Service crashes** | Backend catches the axios error in try/catch | Auto-falls back to `computeFallbackHeuristic()` in JavaScript — same 8-measure logic, same weights. User gets results without knowing the ML service was down |
| **MongoDB disconnects** | Mongoose fires `disconnected` event | `connectDB()` logs the event. Mongoose auto-reconnects by default. If initial connection fails, recursive retry every 5 seconds |
| **JWT expires** | Backend returns 401 | Axios response interceptor catches 401, clears localStorage, redirects to `/login`. User re-authenticates and gets a new 7-day token |
| **Invalid meter readings** | Pydantic validation fails | FastAPI returns 422 with detailed error — e.g., "consumption_kwh must be ≥ 0". Backend surfaces this to the frontend |
| **No readings for meter** | Backend checks `readings.length === 0` | Returns 400: "No readings found for the last 30 days" — clear error message, no crash |
| **Bulk analysis: one meter fails** | `Promise.allSettled()` handles partial failures | Failed meters show error in results array; successful meters still show their analysis. Never fails the entire batch |
| **Frontend loses API connection** | Axios request fails | Toast notification shows error message. Loading spinner stops. User can retry |

---

## 6. Ownership — What YOU Did

> **Be ready to explain your responsibilities, contributions, and decisions**

### My Responsibilities

- **System Architecture**: Designed the 4-service microservice architecture and inter-service communication protocol
- **ML Detection Engine**: Researched and implemented the 8-measure heuristic engine with weighted scoring
- **Training Pipeline**: Built synthetic data generation for 7 theft scenarios and trained the Random Forest model
- **Backend API**: Designed RESTful endpoints, MongoDB schemas with compound indexes, JWT authentication
- **Frontend Dashboard**: Built 7 pages with real-time data visualization using Recharts, state management with Context API
- **DevOps**: Created Docker Compose configuration for one-command deployment of all 4 services

### Key Technical Contributions

1. **The 8-Measure Detection Engine** — This was the core intellectual contribution. I studied electricity theft research papers to identify the 8 most effective detection measures, assigned weights based on detection reliability (consumption drop at 25% because it's the strongest single indicator, frequency deviation at 5% because it's easily caused by grid noise), and added boosting logic so that multi-measure agreement amplifies the signal
2. **Triple-Layer Fallback** — ML model → Python heuristic → JavaScript heuristic. This ensures the system never returns "service unavailable" for a critical infrastructure application
3. **Synthetic Data Pipeline** — Designed 7 realistic theft scenarios with proper hourly consumption patterns (residential morning/evening peaks, commercial 9-to-5 pattern) and variable baselines
4. **Feature Engineering** — Created 10 engineered features beyond basic statistics (zero_peak_ratio, bypass_ratio, night_day_ratio, flat_line_score, etc.) that significantly improved model accuracy
5. **Concurrent Bulk Analysis** — Used `Promise.allSettled()` for fault-tolerant parallel analysis of all meters

### Decisions I Made

- Chose weighted heuristic over pure ML for **explainability** (operators need to understand WHY a meter was flagged)
- Chose microservice over monolith for **independent scaling** (ML service is CPU-heavy, backend is I/O-heavy)
- Chose MongoDB over PostgreSQL for **schema flexibility** (nested anomaly breakdowns, variable telemetry fields)
- Chose JWT over sessions for **stateless horizontal scaling**
- Chose to duplicate the heuristic in both Python and JavaScript for **fault tolerance** over DRY principle

---

## 7. Deep-Dive: ML Detection Engine

### The 8 Measures — Explained Like You Built Them

| # | Measure | Weight | What It Detects | How It Works (Technically) |
|---|---|---|---|---|
| 1 | **Consumption Drop** | 25% | Meter bypass during daytime | Filters readings to peak hours (8AM–8PM), counts zero-kWh readings. Score = `min(1.0, (zero_count / peak_count) × 5)`. Also checks if average consumption dropped below 30% of baseline |
| 2 | **Current Anomaly** | 15% | Physical meter bypass (current shunted around meter) | Counts readings where `current < 0.1A AND voltage > 200V AND consumption > 0`. This is physically impossible without theft — if current is near-zero but voltage is normal and load exists, the meter is being bypassed |
| 3 | **Tamper Detection** | 20% | Hardware tampering with the meter | Uses `tamper_ratio × 10` (so 10% tamper rate → score 1.0). Also detects consecutive tamper flags — 5+ consecutive is scored at 0.9 because random faults are intermittent, sustained tampering is deliberate |
| 4 | **Voltage Anomaly** | 10% | Voltage manipulation to reduce metered consumption | Counts readings outside safe band (190–250V). Extreme outliers (<170V or >270V) are scored more heavily with 5× multiplier |
| 5 | **Power Factor** | 10% | Load manipulation using capacitor banks | Counts readings with PF < 0.5. Cross-references with low consumption — very low PF + low consumption is a strong theft signal |
| 6 | **Pattern Irregularity** | 10% | Reversed or chaotic consumption patterns | Calculates coefficient of variation (std/mean). Also detects day/night inversion — high night consumption + zero day consumption indicates someone is using power but only when inspectors aren't watching |
| 7 | **Frequency Deviation** | 5% | Grid-level anomalies from illegal tapping | Counts readings outside 49–51 Hz. Weighted lower because frequency deviations can have legitimate causes |
| 8 | **Flat-line Detection** | 5% | Spoofed/replayed meter data | Measures unique value count. If a meter reports the exact same consumption for 24 consecutive hours, it's likely sending fake data. Score = `1.0 - (unique_values / total_readings)` |

### Boosting Logic

```python
# If 3+ measures score above 0.5 → multiply by 1.3
if high_measures >= 3:
    theft_probability = min(1.0, theft_probability * 1.3)

# If any single measure is above 0.9 → floor at 40%
if any(v >= 0.9 for v in scores.values()):
    theft_probability = max(0.40, theft_probability)
```

**Why?** If multiple independent measures agree something is wrong, the probability should be higher than what individual weighted scores suggest. And if even one measure is screaming "theft" (0.9+), the overall score should never be below 40%.

### ML Model Training Pipeline

```
train_model.py
    ↓
Generate Synthetic Data (3,000 normal + 600 × 7 anomaly types = 7,200 samples)
    ↓
Extract 24 Features (14 core stats + 10 engineered)
    ↓
Train Random Forest (500 trees, max_depth=25, balanced class weights)
    ↓
Evaluate (accuracy, precision, recall, F1, confusion matrix)
    ↓
5-Fold Cross-Validation
    ↓
Save model.pkl → Auto-loaded by ML service on startup
```

**Key Feature Engineering:**
- `zero_peak_ratio` — Percentage of peak-hour readings with zero consumption
- `bypass_ratio` — Percentage of readings showing current bypass pattern
- `night_day_ratio` — Night avg consumption / Day avg consumption (inversion = theft)
- `flat_line_score` — `1.0 - (unique_values / total_readings)` (closer to 1 = more suspicious)
- `consec_tamper_norm` — Max consecutive tamper flags normalized to 0–1 (÷10)

---

## 8. Deep-Dive: Backend API Design

### Database Schema Design

```
┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Company    │      │      Meter       │      │     Reading      │
├─────────────┤      ├─────────────────┤      ├─────────────────┤
│ _id          │◄────│ company (ref)    │◄────│ meter (ref)      │
│ name         │  1:N │ location         │  1:N │ timestamp        │
│ email        │      │ consumerType     │      │ consumptionKwh   │
│ password     │      │ baselineConsump. │      │ voltage          │
│  (hashed)    │      │ isActive         │      │ current          │
└─────────────┘      └─────────────────┘      │ powerFactor      │
                            │                  │ frequency        │
                            │ 1:N              │ tamperFlag       │
                            ▼                  └─────────────────┘
                     ┌─────────────────┐
                     │      Alert       │
                     ├─────────────────┤
                     │ meter (ref)      │
                     │ timestamp        │
                     │ theftProbScore   │
                     │ anomalyBreakdown │
                     │   ├ consumDrop   │
                     │   ├ voltAnomaly  │
                     │   ├ currAnomaly  │
                     │   ├ pfAnomaly    │
                     │   ├ freqDeviat   │
                     │   ├ tamperDetect │
                     │   ├ patternIrreg │
                     │   └ flatLine     │
                     │ anomalyFlag      │
                     │ status (enum)    │
                     └─────────────────┘
```

### Key Indexing Strategy

```javascript
// Reading: Fast range queries — "last 30 days for meter X"
readingSchema.index({ meter: 1, timestamp: -1 });

// Reading: Aggregation pipeline support
readingSchema.index({ meter: 1, timestamp: 1, consumptionKwh: 1 });

// Meter: Company-scoped queries with active filter
meterSchema.index({ company: 1, isActive: 1 });

// Alert: Status filtering with time ordering
alertSchema.index({ status: 1, createdAt: -1 });
```

**Why these indexes?** Every query in the app is either:
1. "Get readings for meter X in the last N days" → compound index on `{meter, timestamp}`
2. "Get all meters for company Y" → compound index on `{company, isActive}`
3. "Get pending alerts" → compound index on `{status, createdAt}`

### Security Design

| Layer | Implementation |
|---|---|
| **Password Hashing** | bcrypt with salt rounds = 12. `select: false` on password field — never returned in queries by default |
| **JWT** | Signed with secret from env variable. 7-day expiry. Payload: `{ id, name }` |
| **Auth Middleware** | Extracts Bearer token → `jwt.verify()` → attaches `req.company`. All routes except `/auth/*` are protected |
| **Data Isolation** | Every query includes `company: req.company.id` filter |
| **Input Validation** | Mongoose schema validation (min/max, enum, required). Pydantic validation on ML service |
| **CORS** | Configured on both Express and FastAPI |

---

## 9. Deep-Dive: Frontend & UX

### Component Architecture

```
App.jsx (Router)
├── Login.jsx / Register.jsx (Public)
└── AppLayout (Protected — wraps with Sidebar)
    ├── Dashboard.jsx
    │   ├── MetricCard × 4 (Total Meters, Alerts, Resolved, Avg Threat)
    │   ├── ConsumptionChart (Recharts Line)
    │   ├── Anomaly Detection Measures List
    │   └── System Status Panel
    ├── Meters.jsx
    │   └── Meter CRUD (Create/Edit Modal, Delete, Search)
    ├── MeterDetail.jsx
    │   ├── Consumption/Voltage/Current LineChart
    │   ├── "Analyze Anomalies" → ML detection trigger
    │   ├── 8-Measure Breakdown Progress Bars
    │   └── "Add Readings" Modal (simulate data)
    ├── Alerts.jsx
    │   ├── Filterable table (pending/investigating/resolved)
    │   └── One-click status promotion workflow
    └── Reports.jsx
        ├── "Analyze All Meters" → Bulk ML detection
        ├── Risk Bar Chart (sorted by threat score)
        ├── Per-Meter Risk Scorecard Table
        └── CSV Export
```

### State Management — Why Context API Over Redux?

*"The app has only 2 pieces of global state: (1) authenticated user (AuthContext), and (2) toast notifications (ToastContext). Redux would be overkill — it adds boilerplate for state that's simple enough for `useState` + Context. Each page fetches its own data on mount with `useEffect` + the `api` Axios instance. No cross-page shared data needed."*

### Key UX Decisions

1. **Axios Interceptor for Auth** — Token is automatically attached to every request. On 401, user is auto-redirected to login. Zero manual token management in components
2. **Toast Notifications** — Custom `ToastContext` provides `toast.success()`, `toast.error()`, `toast.warning()`, `toast.info()` — used throughout for async operation feedback
3. **Time Range Selector** — MeterDetail has 7/14/30 day toggle. Readings are aggregated by day (summing consumption, averaging voltage/current) for chart clarity
4. **Color-Coded Risk** — Consistent 4-tier color scheme across all pages: 🟢 Green (Low) → 🟡 Amber (Medium) → 🟠 Orange (High) → 🔴 Red (Critical)
5. **Animated Breakdowns** — Anomaly measure bars animate on appear with `transition-all duration-700 ease-out` — makes the analysis feel dynamic

---

## 10. Deep-Dive: DevOps & Deployment

### Docker Compose Architecture

```yaml
4 Services on 1 Bridge Network (theft-net):
  mongo:     MongoDB 7 + healthcheck (ping every 10s)
  backend:   Node.js  (depends_on: mongo [healthy])
  ml-service: FastAPI  (independent)
  frontend:  React    (depends_on: backend)
```

**Key Docker decisions:**
- `mongo` has a health check — `backend` only starts after MongoDB is ready (prevents connection race conditions)
- `ml-service` is independent — it has no database dependency and can start/restart without affecting other services
- Named volume `mongo-data` persists data across container restarts
- All services on `theft-net` bridge network for DNS-based service discovery (backend connects to `mongodb://mongo:27017`)

### Environment Variable Strategy

| Variable | Purpose | Security Note |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | In production: use MongoDB Atlas connection string with auth |
| `JWT_SECRET` | Token signing key | Must be changed from default in production |
| `ML_SERVICE_URL` | ML service endpoint | Uses Docker DNS in containers, localhost in dev |
| `VITE_API_URL` | Frontend → Backend URL | Build-time variable, embedded in client bundle |

---

## 11. Common Interview Questions & Answers

### Q: "How does your ML model handle imbalanced data?"

*"I use `class_weight='balanced'` in the Random Forest, which automatically adjusts weights inversely proportional to class frequencies. My synthetic dataset has 3,000 normal vs 4,200 anomalous samples (600 × 7 types), so it's actually slightly anomaly-heavy, but the balanced class weights handle this. Additionally, the heuristic engine doesn't depend on data balance at all — it uses deterministic rules."*

### Q: "What would happen if a power company has 10,000 meters?"

*"The bulk analysis uses `Promise.allSettled()` which runs all meter analyses concurrently. At 10,000 meters, this could overwhelm the ML service. I'd add: (1) Rate limiting — batch meters in groups of 50-100 with delays between batches; (2) A job queue (Bull/BullMQ with Redis) so the bulk analysis runs asynchronously and reports progress; (3) Consider using the JavaScript fallback heuristic for initial triage and only sending high-risk meters to the ML service."*

### Q: "How do you handle data quality issues in meter readings?"

*"At three levels: (1) **Mongoose schema validation** — consumptionKwh ≥ 0, powerFactor 0–1, frequency ≥ 0; (2) **Pydantic validation** on the ML service — rejects malformed payloads with 422 errors; (3) **Algorithm robustness** — the heuristic handles edge cases: division by zero guards (checks `if mean > 0`), empty readings return probability 0.0 immediately, `_get_hour()` defaults to midday if timestamp parsing fails."*

### Q: "What's the difference between your heuristic and your ML model?"

*"The heuristic is **deterministic and explainable** — given the same readings, it always returns the same result, and you can see exactly which measure fired and why. It uses hand-tuned weights based on domain knowledge. The ML model is **learned and higher accuracy** — it discovers patterns in the 24-dimensional feature space that the heuristic might miss (like complex interactions between bypass_ratio and night_day_ratio). In production, the ML model makes the prediction but the heuristic always runs to provide the breakdown visualization."*

### Q: "How would you make this production-ready?"

*"Key additions: (1) **Rate limiting** on API endpoints (express-rate-limit); (2) **HTTPS** with SSL certificates; (3) **MongoDB authentication** and network restrictions; (4) **Logging/monitoring** — ELK stack or Datadog for centralized logging, Prometheus + Grafana for metrics; (5) **CI/CD pipeline** — GitHub Actions for automated testing and Docker image builds; (6) **Real-time streaming** — replace polling with WebSockets or SSE for live meter updates; (7) **Role-based access** — different permissions for admins vs read-only operators; (8) **Proper secrets management** — HashiCorp Vault or AWS Secrets Manager instead of .env files."*

### Q: "Why is your project called 'theft detection' and not 'loss detection'?"

*"Technical losses (transformer losses, transmission line resistance) are predictable and follow physics-based models. Non-technical losses (theft) create anomalous patterns that deviate from expected behavior. My system specifically targets the anomalous deviations — meter bypassing, tampering, data spoofing — which are deliberate theft activities, not normal grid losses."*

### Q: "Walk me through the code of one specific feature end-to-end"

*"Let me walk through the Analyze Anomalies feature:*

*1. **Frontend** (`MeterDetail.jsx`): The `handleAnalyze()` function calls `api.post('/analyze/${id}')`. While waiting, it shows a loading spinner via the `analyzing` state. On success, it updates `analysisResult` state and shows a toast.*

*2. **Backend** (`routes/analyze.js`): The `/:meterId` POST handler: (a) verifies meter ownership via `Meter.findOne({ _id, company })`, (b) fetches 30 days of readings with `Reading.find()`, (c) computes stats using a `stats()` helper that calculates mean/std/min/max for each dimension, (d) formats the payload with snake_case keys matching the Python schemas, (e) POSTs to the ML service with a 15s timeout, (f) if anomaly detected, creates an Alert document in MongoDB.*

*3. **ML Service** (`model.py`): The `predict_heuristic()` function runs 8 independent analysis loops over the readings array, each computing a 0–1 score, then combines them with weighted averaging and boosting logic.*

*4. **Back to Frontend**: The result flows back through the same chain. If `anomalyDetected` is true, the UI renders a red alert banner with 8 progress bars showing each measure's score, color-coded green/amber/red based on severity."*

---

## 12. What I Would Change Now

> **Always have this answer ready — it shows self-awareness and growth**

| Area | Current State | What I'd Change | Why |
|---|---|---|---|
| **Real-time** | Polling on page load | WebSocket / SSE for live meter updates | Operators need instant alerts, not "refresh to see new data" |
| **Queue System** | Synchronous bulk analysis | Redis + BullMQ job queue | Bulk analysis of 1000+ meters would timeout the HTTP request |
| **Testing** | No automated tests | Jest for backend, Pytest for ML, Playwright for E2E | Can't safely refactor or deploy without test coverage |
| **Heuristic Duplication** | Same algorithm in Python + JS | Single implementation in Python; remove JS fallback or generate it | Code duplication is a maintenance risk |
| **Data Pipeline** | Manual seed script | Apache Kafka for real-time meter data streaming | Production smart meters send data continuously, not in batches |
| **Model Versioning** | Single model.pkl file | MLflow for experiment tracking and model registry | Need to A/B test models and roll back if new model performs worse |
| **RBAC** | Single role (company admin) | Admin / Operator / Viewer roles | Different people need different access levels |
| **Caching** | No caching | Redis cache for dashboard stats and recent readings | Dashboard stats are recalculated on every page load — wasteful |

---

> [!TIP]
> **Final interview tip**: Don't memorize this document word-for-word. Understand the *why* behind every decision. When asked about any component, you should be able to naturally explain:
> **What?** → **Why?** → **Alternatives?** → **Trade-off?** → **What would I change now?**

> A strong project explanation isn't a memorized speech. It's being able to clearly explain what you built, why you built it, and how you solved the problems along the way.
