from __future__ import annotations

from pathlib import Path
import sys
import csv
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from scraper import load_sample_data, refresh_data
from feature_engineering import build_features
from predictor import predict_from_features
from explainer import build_explanation



app = FastAPI(title="Quantum Stocks Predictor Starter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def assemble_payload():
    data = load_sample_data()
    features = build_features(data)
    prediction = predict_from_features(features)
    explanation = build_explanation(features, prediction)
    return {
        "data": data,
        "features": features,
        "prediction": prediction,
        "explanation": explanation
    }


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TRAINING_FILE = DATA_DIR / "training_data.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def log_features(features):
    file_exists = TRAINING_FILE.exists()

    with open(TRAINING_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "basket_momentum",
                "momentum_strength",
                "avg_relative_volume",
                "volume_spike_ratio",
                "avg_volatility",
                "volatility_trend",
                "avg_news_sentiment",
                "positive_ticker_ratio",
                "qqq_change_pct",
                "agreement_strength",
                "leader_gap",
                "label"
            ])

        writer.writerow([
            datetime.utcnow().isoformat(),
            features.get("basket_momentum"),
            features.get("momentum_strength"),
            features.get("avg_relative_volume"),
            features.get("volume_spike_ratio"),
            features.get("avg_volatility"),
            features.get("volatility_trend"),
            features.get("avg_news_sentiment"),
            features.get("positive_ticker_ratio"),
            features.get("qqq_change_pct"),
            features.get("agreement_strength"),
            features.get("leader_gap"),
            ""
        ])

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Quantum predictor backend is running."}


@app.get("/api/data")
def get_data():
    return load_sample_data()


@app.get("/api/features")
def get_features():
    return build_features(load_sample_data())


@app.get("/api/predict")
def get_prediction():
    payload = assemble_payload()
    return payload


@app.post("/api/refresh")
def refresh():
    new_data = refresh_data()
    features = build_features(new_data)
    prediction = predict_from_features(features)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
