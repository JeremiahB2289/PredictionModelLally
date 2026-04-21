from __future__ import annotations

from pathlib import Path
import sys

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
    explanation = build_explanation(features, prediction)
    return {
        "data": new_data,
        "features": features,
        "prediction": prediction,
        "explanation": explanation
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
