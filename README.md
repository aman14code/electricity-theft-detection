# ⚡ PowerGuard — Electricity Theft Detection System

A full-stack, ML-powered platform for detecting electricity theft from smart meter telemetry data.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Stack](https://img.shields.io/badge/stack-Node.js%20%7C%20React%20%7C%20Python-blueviolet)
![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white)

---

## 🏗️ Architecture

```
┌─────────────────┐   REST API    ┌─────────────────────┐   /predict   ┌──────────────────┐
│  React Frontend  │ ─────────── ▶ │  Node.js/Express API │ ──────────▶ │  FastAPI ML Svc  │
│  (Vite, Tailwind)│              │   (Auth, CRUD, Logic) │            │  (Heuristic + ML) │
└─────────────────┘              └──────────┬──────────┘             └──────────────────┘
                                            │ mongoose
                                   ┌────────▼────────┐
                                   │     MongoDB      │
                                   └─────────────────┘
```

### Services

| Service | Tech | Port | Description |
|---|---|---|---|
| **Frontend** | React 18 + Vite + TailwindCSS | 5173 | Dashboard, meters, alerts, reports |
| **Backend** | Node.js + Express | 5000 | REST API, JWT auth, MongoDB ORM |
| **ML Service** | Python + FastAPI | 8000 | 8-measure anomaly detection engine |
| **Database** | MongoDB 7 | 27017 | Meters, readings, alerts, companies |

---

## 🚀 Quick Start

### Option A: Docker Compose (Recommended)

```bash
# Clone the repo
git clone <repo-url>
cd "theif detection"

# Start all 4 services (MongoDB, Backend, ML Service, Frontend)
docker compose up --build

# Seed demo data (in a separate terminal after services are running)
docker exec theft-backend node src/utils/seedData.js
```

Then open **http://localhost:3000**

### Option B: Local Development

**Prerequisites:** Node.js ≥ 18, Python ≥ 3.10, MongoDB running on port 27017

**1. Backend**
```bash
cd backend
cp .env.example .env          # edit MONGO_URI / JWT_SECRET if needed
npm install
npm run seed                  # seed demo data
npm run dev                   # starts on http://localhost:5000
```

**2. ML Service**
```bash
cd ml-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev                   # starts on http://localhost:5173
```

---

## 🔑 Demo Credentials

| Field | Value |
|---|---|
| Email | `admin@powerguard.io` |
| Password | `password123` |

---

## 📊 Features

### Dashboard
- Real-time KPI cards (total meters, active alerts, resolved, avg threat score)
- 7-day network consumption chart
- Active anomaly detection measures list
- System service status

### Smart Meters
- Register / edit / delete meters (residential or commercial)
- Location-based search
- Active/inactive status indicators

### Meter Detail
- Time-range selectable charts (7 / 14 / 30 days)
- Consumption, voltage & current trend lines
- **Analyze Anomalies** — runs ML detection and shows per-measure breakdown
- **Add Readings** — manually ingest simulated hourly readings (great for demos)

### Theft Alerts
- Filter by status: pending / investigating / resolved
- One-click status promotion workflow
- Theft probability scores with color-coded risk levels
- Link to offending meter

### Reports & Analytics
- **Bulk Analyze All Meters** — runs ML detection across entire network
- Bar chart of threat scores sorted by risk
- Per-meter risk scorecard with probability mini-bars
- CSV export of analysis results

---

## 🤖 ML Detection Engine

The ML service uses an **8-measure weighted heuristic engine** (with optional trained model fallback):

| # | Measure | Weight | Description |
|---|---|---|---|
| 1 | Consumption Drop | 25% | Zero kWh during peak daylight hours |
| 2 | Current Anomaly | 15% | Near-zero current + normal voltage (bypass) |
| 3 | Tamper Detection | 20% | Hardware tamper flags from meter |
| 4 | Voltage Anomaly | 10% | Outside safe 190–250V band |
| 5 | Power Factor Anomaly | 10% | Unusually low PF suggesting load manipulation |
| 6 | Pattern Irregularity | 10% | Statistical deviation from expected patterns |
| 7 | Frequency Deviation | 5% | Grid frequency outside 49–51 Hz |
| 8 | Flat-line Detection | 5% | Suspiciously constant readings (spoofed meter) |

**Risk thresholds:**
- 🟢 **Low** — < 30% probability
- 🟡 **Medium** — 30–49%
- 🟠 **High** — 50–74%
- 🔴 **Critical** — ≥ 75%

To use a **trained model**, drop a scikit-learn `.pkl` file at `ml-service/models/model.pkl`. The service will automatically use it and fall back to the heuristic if unavailable.

---

## 🌱 Seed Data

The seed script creates:
- 1 demo company
- 8 smart meters (6 normal + 2 suspicious)
- 30 days × 24 hours = **5,952 readings** per meter
- Anomalous data injected into:
  - **Meter 7** (Sunset Colony): zero consumption during peak hours
  - **Meter 8** (Old Factory Road): voltage tampering + tamper flags

---

## 📁 Project Structure

```
theif detection/
├── backend/                 # Node.js/Express API
│   ├── src/
│   │   ├── config/db.js     # MongoDB connection with retry
│   │   ├── middleware/auth.js # JWT middleware
│   │   ├── models/          # Mongoose schemas
│   │   ├── routes/          # Express route handlers
│   │   └── utils/seedData.js # Demo data seeder
│   ├── .env.example
│   └── Dockerfile
├── frontend/                # React + Vite
│   ├── src/
│   │   ├── api/axios.js     # Axios instance with JWT interceptor
│   │   ├── components/      # Sidebar, MetricCard, ConsumptionChart, Toast
│   │   ├── context/         # AuthContext, ToastContext
│   │   └── pages/           # Dashboard, Meters, MeterDetail, Alerts, Reports
│   └── Dockerfile
├── ml-service/              # Python FastAPI ML microservice
│   ├── app/
│   │   ├── main.py          # FastAPI app + /predict endpoint
│   │   ├── model.py         # Heuristic engine + model loader
│   │   └── schemas.py       # Pydantic request/response schemas
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🔌 API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register company |
| POST | `/api/auth/login` | Login & get JWT |

### Meters
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/meters` | List all meters |
| POST | `/api/meters` | Create meter |
| PUT | `/api/meters/:id` | Update meter |
| DELETE | `/api/meters/:id` | Delete meter |

### Readings
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/readings` | Bulk insert readings |
| GET | `/api/readings/:meterId?days=7` | Get readings for meter |

### Alerts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/alerts?status=pending` | List alerts (filterable) |
| PATCH | `/api/alerts/:id` | Update alert status |

### Analysis
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analyze/:meterId` | Analyze single meter |
| POST | `/api/analyze/bulk` | Analyze all meters |

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/stats` | KPI metrics |
| GET | `/api/dashboard/consumption` | 7-day consumption data |

---

## ⚙️ Environment Variables

### Backend (`.env`)

```env
PORT=5000
NODE_ENV=development
MONGO_URI=mongodb://localhost:27017/theft_detection
JWT_SECRET=your-256-bit-secret
JWT_EXPIRES_IN=7d
ML_SERVICE_URL=http://localhost:8000
```

### Frontend (`.env` or Docker env)
```env
VITE_API_URL=http://localhost:5000
```

---

## 📜 License

MIT © PowerGuard Team
