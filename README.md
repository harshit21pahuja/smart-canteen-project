# 🍽️ Smart Canteen - AI-Powered Food Waste Reduction & Meal Management System

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20Supabase-3ECF8E.svg)](https://supabase.com/)
[![TextBlob](https://img.shields.io/badge/NLP-TextBlob-yellowgreen.svg)](https://textblob.readthedocs.io/)
[![Deployment](https://img.shields.io/badge/Deploy-Render%20Live-brightgreen.svg)](https://smart-canteen-project-khfa.onrender.com)

An intelligent, full-stack campus dining and food optimization system designed to tackle university/hostel food waste. By combining **predictive demand forecasting**, **conflict-free digital meal bookings**, **NLP student feedback analysis**, and **computer vision plate waste monitoring**, Smart Canteen empowers kitchen management to cook the exact required portions while giving students a frictionless dining portal.

---

## 🌐 Live Production Deployment

🔗 **Live URL:** [https://smart-canteen-project-khfa.onrender.com](https://smart-canteen-project-khfa.onrender.com)

Hosted on **Render.com** (Python/Gunicorn) connected to **Supabase Cloud PostgreSQL**.

---

## 🚀 Live Demo & Ready Credentials

For recruiters, evaluators, and reviewers testing the application:

| Role | Portal URL | Username / Roll | Password / Phone | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | [`/admin`](https://smart-canteen-project-khfa.onrender.com/admin) | `admin` | `admin123` | Full dashboard, AI metrics, and simulation controls |
| **Demo Student** | [`/login`](https://smart-canteen-project-khfa.onrender.com/login) | `101` | `9876543210` | Pre-registered test account *(OTP displays on screen)* |
| **New Student** | [`/register`](https://smart-canteen-project-khfa.onrender.com/register) | *Any custom Roll* | *Any 10-digit Phone* | Self-registration flow with profile management |

> 💡 **Demo OTP Note:** Live SMS via Twilio is optional. In testing mode, the 6-digit OTP is automatically shown on-screen and logged to the server terminal.

---

## 🌟 Key Features

### 1. 🎓 Student Dining Portal & Duplicate-Free Booking
- **Conflict-Free Reservation:** Students reserve daily preferences (Breakfast, Lunch, Snacks, Dinner). Database-level constraints prevent accidental duplicate bookings for the same day.
- **Dynamic Edit Mode:** If already booked, the system displays their confirmed choices and allows seamless updating of preferences before cutoff time.
- **Glassmorphic UI:** Built with custom vanilla CSS, smooth micro-animations, Outfit typography, and Bennett University branding.

### 2. 📈 Time-Series AI Demand Forecasting
- **Linear Regression Prediction:** Located in [`ai_models/meal_predictor.py`](code/ai_models/meal_predictor.py).
- **Adaptive Volume Scaling:** 
  - In low-volume testing (1–5 students), the model realistically projects demand based on confirmed counts plus an intelligent walk-in safety buffer (+1).
  - In high-volume operations (50+ students), the engine applies time-series regression trained over 30-day historical meal trends with dynamic confidence scoring.

### 3. 🧠 NLP Student Feedback & Sentiment Analysis
- **TextBlob Integration:** Located in [`ai_models/sentiment_analyzer.py`](code/ai_models/sentiment_analyzer.py).
- **Categorization:** Automatically classifies student meal reviews into **Positive**, **Neutral**, and **Negative** sentiment buckets with polarity scoring.
- **Actionable Insights:** Displays percentage satisfaction metrics on the Admin Dashboard to guide kitchen menu improvements.

### 4. 📸 AI Plate Scanner & Waste Tracking
- **Food Leftover Monitoring:** Located in [`ai_models/waste_detector.py`](code/ai_models/waste_detector.py).
- **Visual Log Analysis:** Enables staff to upload tray images post-dining to log leftover percentages, directly correlating prepared quantities with actual consumption.

### 5. 🛠️ Canteen Traffic Simulator (Admin Tool)
- **One-Click 50+ Student Load:** Test full university traffic instantly (`Load 50+ Students`) to view realistic high-volume predictions and NLP review queues.
- **One-Click Clean Reset:** Instant rollback (`Reset to Original`) to a clean state.

---

## 🏗️ Technology Architecture

```
smart-canteen-project/
├── code/
│   ├── ai_models/
│   │   ├── meal_predictor.py       # Time-series demand forecasting engine
│   │   ├── menu_recommender.py     # Waste-aware meal suggestion algorithm
│   │   ├── sentiment_analyzer.py   # TextBlob NLP feedback classifier
│   │   └── waste_detector.py       # Computer Vision plate heuristic model
│   ├── static/                     # CSS design system, logos, visual assets
│   ├── templates/                  # Jinja2 HTML5 semantic templates
│   ├── app.py                      # Core Flask WSGI application & route logic
│   ├── update_db.py                # Schema migrations & database sync engine
│   └── requirements.txt            # Application dependencies
├── deployment/                     # Deployment mirror & artifacts
├── Procfile                        # Gunicorn production start configuration
├── render.yaml                     # Render.com blueprint configuration
├── requirements.txt                # Root dependencies for cloud platform buildpacks
└── README.md                       # Comprehensive documentation
```

### Tech Stack
- **Backend:** Python 3.13, Flask 3.1, Gunicorn (Production WSGI)
- **Machine Learning & NLP:** Scikit-Learn, NumPy, TextBlob
- **Database:** Dual-engine architecture: Managed Cloud PostgreSQL ([Supabase](https://supabase.com)) with automatic schema migrations + Local SQLite fallback
- **Security & Communications:** Session cookies, Twilio SMS API integration (simulated & live ready)
- **Styling:** Vanilla CSS Glassmorphism design tokens (no bulky dependencies)

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.10+ installed

### Setup
```bash
# 1. Clone repository
git clone https://github.com/harshit21pahuja/smart-canteen-project.git
cd smart-canteen-project

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
cd code
python app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## ☁️ Cloud Deployment Guide

This project is pre-configured with `Procfile`, `render.yaml`, and production `gunicorn` for **1-click free deployment**.

### Option A: Deploy on Render.com (Recommended - 100% Free)
1. Push your repository to GitHub.
2. Sign in to **[Render.com](https://render.com)**.
3. Click **New +** $\rightarrow$ **Web Service**.
4. Select your `smart-canteen-project` repository.
5. Render will automatically detect the settings:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --chdir code app:app`
6. Click **Deploy Web Service**. You will receive an active HTTPS link (e.g. `smart-canteen.onrender.com`).

### Option B: Deploy on Railway.app
1. Create a new project on **[Railway.app](https://railway.app)**.
2. Select **Deploy from GitHub Repo**.
3. Railway automatically detects the `Procfile` and launches the application.

---

## 🔮 Future Expansion Roadmap (Scale & Production)

Planned features for transitioning Smart Canteen into an enterprise-grade institutional platform:

- [ ] **Dynamic QR Code Check-in:** Generate an encrypted, single-use QR pass on student profiles upon booking; canteen staff scans the code at meal counters to record attendance and stop proxy collections.
- [ ] **YOLOv8 Deep Learning Plate Analyzer:** Replace heuristic vision weights with a fine-tuned YOLOv8 model for real-time segmented food detection on canteen trays.
- [ ] **Automated Kitchen Raw Material Calculator:** Translate predicted meal demand into automated kitchen grocery orders (e.g. *60 Lunches $\rightarrow$ 12 kg Basmati Rice, 6 kg Dal, 8 kg Paneer*).
- [ ] **Automated WhatsApp / Telegram Notifications:** Automated reminders via WhatsApp Cloud API before evening cut-off times (*"Tomorrow's breakfast is Aloo Paratha — tap [Confirm] before 10 PM"*).
- [ ] **Cloud Database Migration:** Migrate SQLite to Managed **PostgreSQL (Supabase / Neon)** with connection pooling.
- [ ] **Institutional Single Sign-On (SSO):** Integration with Google Workspace / Microsoft Entra ID for university email authentication.

---

## 📄 License
This project is open-source and developed for academic and operational food waste reduction demonstration.
