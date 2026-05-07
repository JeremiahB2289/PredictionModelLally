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
