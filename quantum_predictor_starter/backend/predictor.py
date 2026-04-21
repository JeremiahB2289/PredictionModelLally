"""Basic starter prediction logic.

This is intentionally simple so your team can replace it later.
"""

from __future__ import annotations

from typing import Any, Dict


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def predict_from_features(features: Dict[str, Any]) -> Dict[str, Any]:
    score = 0.0

    score += features.get("basket_momentum", 0.0) * 0.35
    score += (features.get("avg_relative_volume", 1.0) - 1.0) * 1.8
    score += (features.get("avg_news_sentiment", 0.5) - 0.5) * 7.0
    score += features.get("qqq_change_pct", 0.0) * 0.6
    score += (features.get("positive_ticker_ratio", 0.0) - 0.5) * 4.0

    if features.get("market_session") == "premarket":
        score += 0.4
    if features.get("avg_volatility", 0.0) > 7.0:
        score -= 0.5

    predicted_direction = "UP" if score >= 0 else "DOWN"
    expected_move_pct = clamp(abs(score) * 0.9, 0.2, 8.0)
    confidence = clamp(50 + abs(score) * 8, 51, 96)
    risk_level = "High" if features.get("avg_volatility", 0.0) >= 6 else "Moderate"
    if confidence >= 80 and risk_level != "High":
        risk_level = "Low-Moderate"

    return {
        "predicted_direction": predicted_direction,
        "confidence_pct": round(confidence, 1),
        "expected_move_pct": round(expected_move_pct, 2),
        "risk_level": risk_level,
        "score": round(score, 3),
        "prediction_horizon": "next 15 minutes"
    }
