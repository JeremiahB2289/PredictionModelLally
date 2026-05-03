# Quantum Stocks Predictor Starter

A basic end-to-end starter project for a **quantum stocks short-term movement predictor** focused on QBTS, QUBT, IONQ, and RGTI.

This is meant to be a working foundation that your team can improve piece by piece.

## What is included

- **Scraper layer**: tries to pull live data with `yfinance`; falls back to sample JSON
- **JSON/data layer**: stores stock snapshots in `data/sample_market_data.json`
- **Feature engineering layer**: builds a few simple features from the raw stock data
- **ML layer**: generates a basic prediction and confidence score
- **Explanation layer**: creates a simple human-readable reason for the prediction
- **Frontend**: dashboard showing prices, features, prediction, confidence, and news

## Project structure

```text
quantum_predictor_starter/
├── backend/
│   ├── app.py
│   ├── scraper.py
│   ├── feature_engineering.py
│   ├── predictor.py
│   └── explainer.py
├── data/
│   └── sample_market_data.json
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
└── start.sh
```

## How it works

Pipeline:

**Scraper/API -> JSON -> Feature Engineering -> Prediction -> Explanation -> Frontend**

## Quick start

### 1. Create a virtual environment

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the backend

```bash
cd backend
python app.py
```

The API will start on:

```text
http://127.0.0.1:8000
```

### 4. Open the frontend

Either:
- open `frontend/index.html` directly in your browser, or
- serve it locally with a simple server

```bash
cd frontend
python3 -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500
```

## API routes

- `GET /api/health` -> basic status
- `GET /api/data` -> raw market/news data
- `GET /api/features` -> engineered features
- `GET /api/predict` -> prediction output
- `POST /api/refresh` -> attempts fresh data pull

## Notes

### Current ML logic
Right now the "model" is intentionally simple. It uses a weighted score based on:
- basket momentum
- average relative volume
- news sentiment
- average volatility
- whether premarket/postmarket is active

This is enough for a demo and gives you a clear place to replace it later with:
- logistic regression
- random forest
- XGBoost
- LSTM / time-series model
- graph-based sector movement model

### Current explanation logic
The explanation layer is rule-based right now. Later you can replace it with:
- OpenAI API
- Claude API
- local LLM

### Good next upgrades
- pull intraday candles instead of just snapshots
- store time-series data in SQLite or Supabase
- add real news sentiment scoring
- train on historical labeled data
- add leader/laggard detection across the 4 stocks
- add a custom quantum sector index
- add model performance tracking

## Suggested team split

- **Person 1:** data collection and cleaning
- **Person 2:** features and model
- **Person 3:** frontend/dashboard

## Deploying to a Live Server with Vercel
To move beyond localhost and deploy this quantum stocks predictor to a live server, Vercel offers the simplest path for full-stack deployment. Backend deployment: Your FastAPI backend needs to be deployed separately since Vercel's serverless functions work best with Python. Create a new api/index.py file in your project root that imports your FastAPI app and uses Vercel's ASGI adapter. Add a vercel.json configuration file in the root directory with build settings pointing to your Python runtime and defining the rewrite rules for your API endpoints. Push your code to GitHub, then import the repository on Vercel - it will automatically detect and deploy the Python serverless functions. Your backend will then be accessible at a live URL like https://your-project.vercel.app/api/predict. Frontend deployment: Change the API_BASE variable in frontend/app.js from http://127.0.0.1:8000 to your live Vercel backend URL (e.g., https://your-project.vercel.app). Since Vercel hosts both frontend and backend under the same domain, you can also use a relative path like /api instead of a full URL to avoid CORS issues. Simply push your entire project to GitHub, connect the repository to Vercel, and it will automatically deploy your static frontend files (HTML, CSS, JS) alongside the serverless API functions. The CORS headers already configured in your app.py (allow_origins=["*"]) will work seamlessly with Vercel's deployment. For production, add environment variables in Vercel's dashboard for any sensitive data (API keys, database credentials) and consider adding rate limiting to prevent excessive yfinance calls from overwhelming your free tier limits.

