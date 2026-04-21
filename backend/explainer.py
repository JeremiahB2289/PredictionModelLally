"""Simple explanation layer.

This is rule-based for now. Later you can replace it with a real LLM call.
"""

from __future__ import annotations

from typing import Any, Dict


def build_explanation(features: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    reasons = []

    if features.get("basket_momentum", 0) > 0:
        reasons.append("the quantum basket is moving higher together")
    else:
        reasons.append("the quantum basket is weakening together")

    if features.get("avg_relative_volume", 1) > 1.2:
        reasons.append("relative volume is elevated")

    if features.get("avg_news_sentiment", 0.5) > 0.55:
        reasons.append("news tone is positive")
    elif features.get("avg_news_sentiment", 0.5) < 0.45:
        reasons.append("news tone is negative")

    if features.get("qqq_change_pct", 0) > 0:
        reasons.append("broader tech is helping")
    elif features.get("qqq_change_pct", 0) < 0:
        reasons.append("broader tech is acting as a headwind")

    leader = features.get("leader")
    laggard = features.get("laggard")
    if leader and laggard and leader != laggard:
        reasons.append(f"{leader} is currently leading while {laggard} is lagging")

    joined = ", ".join(reasons[:-1]) + (", and " + reasons[-1] if len(reasons) > 1 else reasons[0])

    return (
        f"Model expects {prediction['predicted_direction']} movement over the {prediction['prediction_horizon']} because "
        f"{joined}."
    )
