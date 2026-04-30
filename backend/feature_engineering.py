"""Feature engineering layer."""

from __future__ import annotations
from typing import Any, Dict, List


def build_features(data: Dict[str, Any]) -> Dict[str, Any]:
    stocks: List[Dict[str, Any]] = data.get("stocks", [])
    macro: Dict[str, Any] = data.get("macro", {})

    if not stocks:
        return {
            "basket_momentum": 0.0,
            "momentum_strength": 0.0,
            "leader_gap": 0.0,
            "avg_relative_volume": 1.0,
            "volume_spike_ratio": 0.0,
            "avg_volatility": 0.0,
            "volatility_trend": 0.0,
            "avg_news_sentiment": 0.5,
            "positive_ticker_ratio": 0.0,
            "agreement_strength": 0.0,
            "momentum_agreement": 0.0,
            "volatility_adjusted_momentum": 0.0,
            "market_session": data.get("market_session", "unknown"),
            "qqq_change_pct": 0.0,
            "leader": None,
            "laggard": None
        }

    n = len(stocks)

    # --- core stats ---
    basket_momentum = sum(s["change_pct"] for s in stocks) / n
    momentum_strength = sum(abs(s["change_pct"]) for s in stocks) / n

    avg_relative_volume = sum(
        (s["volume"] / s["avg_volume"]) if s["avg_volume"] else 1.0
        for s in stocks
    ) / n

    avg_volatility = sum(s["volatility"] for s in stocks) / n

    avg_news_sentiment = sum(s["news_sentiment"] for s in stocks) / n

    positive_ticker_ratio = sum(1 for s in stocks if s["change_pct"] > 0) / n

    # --- ordering ---
    sorted_by_change = sorted(stocks, key=lambda x: x["change_pct"])
    leader = sorted_by_change[-1]["ticker"]
    laggard = sorted_by_change[0]["ticker"]

    leader_change = sorted_by_change[-1]["change_pct"]
    laggard_change = sorted_by_change[0]["change_pct"]

    # safer normalization
    leader_gap = (leader_change - laggard_change) / (abs(leader_change) + abs(laggard_change) + 1e-6)

    # --- signals ---
    volume_spike_ratio = sum(
        1 for s in stocks if s["volume"] > s["avg_volume"] * 1.5
    ) / n

    volatility_trend = sum(
        1 for s in stocks if s["volatility"] > 5.0
    ) / n

    agreement_strength = abs(positive_ticker_ratio - 0.5) * 2

    # strong move + strong agreement
    momentum_agreement = basket_momentum * agreement_strength

    # filters noisy high-volatility moves
    volatility_adjusted_momentum = basket_momentum / (avg_volatility + 1e-6)

    return {
        "basket_momentum": round(basket_momentum, 3),
        "momentum_strength": round(momentum_strength, 3),
        "leader_gap": round(leader_gap, 3),
        "avg_relative_volume": round(avg_relative_volume, 3),
        "volume_spike_ratio": round(volume_spike_ratio, 3),
        "avg_volatility": round(avg_volatility, 3),
        "volatility_trend": round(volatility_trend, 3),
        "avg_news_sentiment": round(avg_news_sentiment, 3),
        "positive_ticker_ratio": round(positive_ticker_ratio, 3),
        "agreement_strength": round(agreement_strength, 3),
        "momentum_agreement": round(momentum_agreement, 3),
        "volatility_adjusted_momentum": round(volatility_adjusted_momentum, 3),

        "market_session": data.get("market_session", "unknown"),
        "qqq_change_pct": round(float(macro.get("qqq_change_pct", 0.0)), 3),

        "leader": leader,
        "laggard": laggard
    }