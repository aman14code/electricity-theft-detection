# 🚀 Full-Stack Deployment Guide

All code changes have been **pushed to GitHub** ✅. Now follow these steps to deploy the complete system.

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Vercel (Frontend)  │────▶│  Render (Backend)    │────▶│  Render (ML Service)│
│  React + Vite SPA   │     │  Express + MongoDB   │     │  FastAPI + Model    │
│                     │     │                      │     │                     │
│  electricity-theft- │     │  powerguard-backend  │     │  powerguard-ml-     │
│  detection-sandy    │     │  .onrender.com       │     │  service.onrender   │
│  .vercel.app        │     │                      │     │  .com               │
└─────────────────────┘     └──────────┬───────────┘     └─────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  MongoDB Atlas       │
                            │  Free M0 Cluster     │
                            └─────────────────────┘
```

---

## Step 1: MongoDB Atlas (Free Database)

1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and sign in / create account
2. Click **"Build a Database"** → Select **M0 FREE** tier
3. Choose a region (e.g., Mumbai for India)
4. Set **Database Username** and **Password** (save these!)
5. Under **Network Access** → Click **"Add IP Address"** → Select **"Allow Access from Anywhere"** (`0.0.0.0/0`)
6. Once the cluster is created, click **"Connect"** → **"Drivers"**
7. Copy the connection string. It looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/theft_detection?retryWrites=true&w=majority
   ```
   Replace `<username>` and `<password>` with your actual credentials.

> [!IMPORTANT]
> Save this connection string — you'll need it for the Render backend deployment.

---

## Step 2: Deploy Backend + ML Service on Render

### Option A: One-Click Blueprint (Recommended)

1. Go to [https://render.com](https://render.com) and sign in
2. Go to **Dashboard** → Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo: `aman14code/electricity-theft-detection`
4. Render will detect the `render.yaml` and show 2 services:
   - **powerguard-ml-service** (Python/FastAPI)
   - **powerguard-backend** (Node.js/Express)
5. Click **"Apply"**
6. When prompted, set the **MONGO_URI** environment variable to your MongoDB Atlas connection string from Step 1.

### Option B: Manual Deployment

#### Deploy ML Service First:
1. **New +** → **Web Service** → Connect your repo
2. **Root Directory**: `ml-service`
3. **Runtime**: Python 3
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Plan**: Free
7. Add env var: `MODEL_PATH` = `./models/ensemble_model.pkl`
8. Deploy — note the URL (e.g., `https://powerguard-ml-service.onrender.com`)

#### Deploy Backend:
1. **New +** → **Web Service** → Connect your repo
2. **Root Directory**: `backend`
3. **Runtime**: Node
4. **Build Command**: `npm install`
5. **Start Command**: `npm start`
6. **Plan**: Free
7. Add environment variables:
   | Variable | Value |
   |----------|-------|
   | `NODE_ENV` | `production` |
   | `PORT` | `5000` |
   | `JWT_SECRET` | (any random strong string) |
   | `MONGO_URI` | Your MongoDB Atlas connection string |
   | `ML_SERVICE_URL` | `https://powerguard-ml-service.onrender.com` |
8. Deploy — note the URL (e.g., `https://powerguard-backend.onrender.com`)

---

## Step 3: Update Vercel Frontend

The `vercel.json` already has the API proxy configured to forward `/api/*` to `https://powerguard-backend.onrender.com`. 

**If your Render backend URL is different**, update it:

1. Go to your Vercel project dashboard
2. The auto-deploy should trigger from the GitHub push
3. **If the backend URL differs from `powerguard-backend`**, update `frontend/vercel.json`:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/(.*)",
         "destination": "https://YOUR-ACTUAL-BACKEND-URL.onrender.com/api/$1"
       },
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```

> [!NOTE]
> Vercel should auto-deploy from GitHub. If not, go to Vercel Dashboard → your project → **Deployments** → click **"Redeploy"**.

---

## Step 4: Verify Deployment

### Test Backend Health:
```
https://powerguard-backend.onrender.com/api/health
```
Should return: `{"status":"ok","timestamp":"..."}`

### Test ML Service Health:
```
https://powerguard-ml-service.onrender.com/health
```
Should return: `{"status":"ok","service":"ml-service"}`

### Test ML Metrics:
```
https://powerguard-ml-service.onrender.com/metrics
```
Should return the full evaluation_results.json with all 6 model metrics.

### Test Frontend:
Visit `https://electricity-theft-detection-sandy.vercel.app/`
1. Register a new account → should work (creates user in MongoDB Atlas)
2. Dashboard → should show stats
3. ML Models → should show all model performance charts ✅

---

## What Was Fixed & Pushed

| File | Change |
|------|--------|
| `frontend/vercel.json` | Added API proxy rewrite to route `/api/*` to Render backend |
| `backend/src/server.js` | Configured CORS to allow Vercel domain |
| `ml-service/app/main.py` | Fixed `NameError` — `_ensemble` was used but never imported |
| `render.yaml` | Fixed `runtime` field and `ML_SERVICE_URL` auto-wiring |
| `ml-service/models/model.pkl` | Updated trained model file |

---

> [!WARNING]
> **Render free tier** puts services to sleep after 15 minutes of inactivity. The first request after sleep takes ~30-60 seconds (cold start). This is normal for free tier. Upgrade to paid ($7/month per service) for always-on.

> [!TIP]
> The `ensemble_model.pkl` (178MB) is gitignored because it's too large for GitHub. The ML service will fall back to the heuristic engine for predictions, but the **evaluation metrics** (`evaluation_results.json`) are on GitHub and will display properly in the ML Models page.
