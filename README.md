# TrafficIntel AI - AI-Based Traffic Congestion Prediction Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-RandomForest-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3.svg?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900.svg?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A production-quality traffic intelligence web application that leverages spatiotemporal telemetry, live meteorological fusion, and Random Forest machine learning to forecast urban roadway bottlenecks at 15, 30, and 60-minute horizons.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (HTML5 / Bootstrap 5 / Leaflet.js / Chart.js)"]
        UI_Landing["Landing Page (index.html)"]
        UI_Dash["Command Dashboard (dashboard.html)"]
        UI_Pred["AI Prediction Studio (predictions.html)"]
        UI_Route["Route Planner (route-planner.html)"]
        UI_Reports["Community Hazards (reports.html)"]
        UI_Analytics["Analytics & Metrics (analytics.html)"]
    end

    subgraph Backend["FastAPI REST Backend (Python 3.12)"]
        API_Gateway["API Router (/api)"]
        Auth_Service["JWT & Bcrypt Security"]
        ML_Engine["ML Service (Random Forest Classifier)"]
        Route_Engine["Routing Service (OSRM + Delay Heuristics)"]
        Geo_Service["Geocoding Service (Nominatim OSM)"]
        Weather_Service["Weather Service (Open-Meteo)"]
        Traffic_Service["Telemetry Service (TomTom / OSM Baseline)"]
    end

    subgraph Data["Persistence & Machine Learning"]
        SQL_DB[("Relational DB (MySQL / SQLite Fallback)")]
        ML_Model["Model Artifact (rf_traffic_model.joblib)"]
        ML_Meta["Metadata & Metrics (model_metadata.json)"]
    end

    Client -->|RESTful JSON / Bearer JWT| API_Gateway
    API_Gateway --> Auth_Service
    API_Gateway --> ML_Engine
    API_Gateway --> Route_Engine
    API_Gateway --> Geo_Service
    API_Gateway --> Weather_Service
    API_Gateway --> Traffic_Service

    Auth_Service --> SQL_DB
    ML_Engine --> ML_Model
    ML_Engine --> ML_Meta
    Route_Engine --> SQL_DB
    Traffic_Service --> SQL_DB
```

---

## 2. Key Features

- **Browser Location Detection & Search**: Instant geolocation via HTML5 Geolocation with fallback to Nominatim geocoding auto-suggestions.
- **Real-Time Environmental Synchronization**: Incorporates real-time ambient temperature, humidity, and rainfall from Open-Meteo into congestion forecasting.
- **Multi-Horizon ML Congestion Forecasting**: Predicts categorical congestion tier (`LOW`, `MODERATE`, `HIGH`) at 15, 30, and 60 minutes with calibrated probabilities and confidence scores.
- **Explainable AI (XAI)**: Displays localized feature importance attributions (diurnal rush window, rain intensity, day of week rhythm) explaining why the model predicted a particular tier.
- **Optimal Departure Recommendation**: Calculates whether departing immediately or waiting 15-45 minutes saves commuter travel time.
- **Route Comparison & Delays**: Evaluates primary expressway and alternative arterial bypass routes using OSRM turn-by-turn geometry combined with traffic delay models.
- **Crowdsourced Hazard Feeds**: Enables users to report accidents, road closures, waterlogging, and construction, featuring peer upvoting and automatic decay.
- **Saved Places**: Personal bookmarking of Home, Work, College, and custom hubs.
- **Data Transparency**: Explicitly delineates live external telemetry from offline baselines and model inferences.

---

## 3. Technology Stack

### Frontend
- **HTML5 & Semantic Markup**
- **CSS3 Design System**: Custom slate/navy design tokens, elevation shadows, responsive breakpoints.
- **JavaScript (ES6+)**: Modular client libraries (`api.js`, `auth.js`, `map.js`, `dashboard.js`, `predictions.js`, `routes.js`, `analytics.js`).
- **Bootstrap 5 & Bootstrap Icons**: Clean modern UI without emojis.
- **Leaflet.js & OpenStreetMap**: Interactive mapping, GeoJSON routes, color-coded congestion nodes.
- **Chart.js**: Congestion horizon forecasts, diurnal speed profiles, weekly distributions.

### Backend & Machine Learning
- **Python 3.12**
- **FastAPI**: Asynchronous high-performance RESTful API with automated OpenAPI docs.
- **Pydantic v2**: Strict input validation and serialization schemas.
- **SQLAlchemy ORM**: Relational persistence supporting both MySQL and zero-config SQLite.
- **Bcrypt & Python-Jose**: Secure password hashing and signed JWT authentication.
- **Scikit-Learn & Joblib**: Random Forest Classifier ensemble with balanced class weights.
- **Pandas & NumPy**: Spatiotemporal feature engineering.

### External Integrations
- **Geocoding**: OpenStreetMap Nominatim API (Free, zero-key requirement).
- **Weather**: Open-Meteo Meteorological API (Free real-time temperature, humidity, precipitation).
- **Routing**: Open Source Routing Machine (OSRM) driving API.
- **Traffic Telemetry**: TomTom Traffic Flow API (when API key is supplied) or calibrated OpenStreetMap baseline.

---

## 4. Directory Structure

```text
traffic-congestion-prediction/
├── frontend/                     # Modern responsive user interface
│   ├── index.html                # Landing page & search
│   ├── login.html                # User login with demo autofill
│   ├── register.html             # User registration
│   ├── dashboard.html            # Main command center
│   ├── predictions.html          # Deep ML prediction studio & XAI
│   ├── route-planner.html        # Multi-route comparison
│   ├── reports.html              # Crowdsourced hazards
│   ├── analytics.html            # Metrics & confusion matrix
│   ├── css/
│   │   └── style.css             # Unified mobility design system
│   └── js/
│       ├── api.js                # API request wrapper & endpoints
│       ├── auth.js               # Session & token manager
│       ├── map.js                # Leaflet map manager
│       ├── dashboard.js          # Dashboard controller
│       ├── predictions.js        # Prediction studio controller
│       ├── routes.js             # Route comparison controller
│       └── analytics.js          # Chart.js analytics controller
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── main.py               # Application entrypoint & static mounting
│   │   ├── config.py             # Environment configuration
│   │   ├── database.py           # SQLAlchemy engine & session maker
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── location.py
│   │   │   ├── search.py
│   │   │   ├── prediction.py
│   │   │   ├── report.py
│   │   │   └── model_version.py
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── routers/              # RESTful API route controllers
│   │   ├── services/             # Geocoding, weather, routing, ML services
│   │   ├── ml/artifacts/         # Serialized model & metadata
│   │   └── utils/security.py     # Bcrypt & JWT tokens
│   ├── scripts/
│   │   └── init_db.py            # Database tables & seed data
│   ├── tests/                    # Automated test suite
│   │   ├── test_auth.py
│   │   ├── test_ml.py
│   │   └── test_endpoints.py
│   └── requirements.txt          # Python dependencies
├── ml/                           # Data science pipeline
│   ├── data/traffic_dataset.csv  # 10,000-row telemetry dataset
│   ├── train.py                  # Model training script
│   └── evaluate.py               # Standalone model benchmark
├── run_tests.py                  # Test suite runner
├── .env                          # Local environment variables
├── .env.example                  # Environment template
└── README.md                     # Master documentation
```

---

## 5. Quickstart & Installation (Windows PowerShell)

### Step 1: Install Python Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` if not already present:
```powershell
Copy-Item .env.example .env
```

To configure **MySQL**, edit `.env`:
```ini
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/traffic_prediction_db
```
*(Note: If MySQL is not running locally, the system automatically falls back to SQLite `traffic_intel.db` with zero configuration required).*

### Step 3: Initialize Database & Seed Sample Records
Creates tables and seeds demo account, default saved locations, and sample community reports:
```powershell
python backend/scripts/init_db.py
```

### Step 4: Run Model Evaluation
```powershell
python ml/evaluate.py
```

### Step 5: Run Automated Tests
```powershell
python run_tests.py
```
*(Expected output: **ALL 15 TESTS PASSED SUCCESSFULLY!**)*

### Step 6: Launch the Web Application
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to:
- **Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 6. Pre-Configured Demo Credentials

The database initialization script automatically provisions a demo account for immediate testing:
- **Email**: `demo@trafficintel.ai`
- **Password**: `Traffic@123`

*(A one-click **"Fill Demo Credentials"** button is also available directly on the login page).*

---

## 7. REST API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new user account |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT token |
| `GET` | `/api/auth/me` | Retrieve profile of authenticated user |
| `GET` | `/api/locations/search` | Search places and transit corridors |
| `GET` | `/api/locations/reverse` | Reverse geocode coordinates to address |
| `GET` | `/api/weather` | Retrieve real-time ambient weather parameters |
| `GET` | `/api/traffic` | Retrieve traffic flow and road segments |
| `POST` | `/api/predictions` | Run ML congestion inference (15m, 30m, 60m) |
| `GET` | `/api/predictions/history` | Retrieve past prediction logs |
| `POST` | `/api/routes/compare` | Compare primary vs. alternative routes |
| `GET` | `/api/reports` | Retrieve active crowdsourced road hazards |
| `POST` | `/api/reports` | Submit community road incident |
| `POST` | `/api/reports/{id}/vote` | Upvote and verify community report |
| `GET` | `/api/saved-locations` | List user's saved locations |
| `POST` | `/api/saved-locations` | Save a new location |
| `DELETE`| `/api/saved-locations/{id}` | Delete saved location |
| `GET` | `/api/analytics/traffic` | Empirical congestion distributions & diurnal curve |
| `GET` | `/api/analytics/model-metrics`| Live Random Forest evaluation metrics & confusion matrix |

---

## 8. License & Standards
Developed under the MIT License. Designed for professional mobility intelligence, university technical project demonstrations, and enterprise portfolio showcases.
