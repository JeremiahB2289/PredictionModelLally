"""Feature engineering layer."""

from __future__ import annotations

from typing import Any, Dict, List


def build_features(data: Dict[str, Any]) -> Dict[str, Any]:
    stocks: List[Dict[str, Any]] = data.get("stocks", [])
    macro: Dict[str, Any] = data.get("macro", {})

    if not stocks:
        return {
            "basket_momentum": 0.0,
            "avg_relative_volume": 1.0,
            "avg_volatility": 0.0,
            "avg_news_sentiment": 0.5,
            "positive_ticker_ratio": 0.0,
            "market_session": data.get("market_session", "unknown"),
            "qqq_change_pct": 0.0,
            "leader": None,
            "laggard": None
        }

    basket_momentum = sum(stock["change_pct"] for stock in stocks) / len(stocks)
    avg_relative_volume = sum(
        (stock["volume"] / stock["avg_volume"]) if stock["avg_volume"] else 1.0
        for stock in stocks
    ) / len(stocks)
    avg_volatility = sum(stock["volatility"] for stock in stocks) / len(stocks)
    avg_news_sentiment = sum(stock["news_sentiment"] for stock in stocks) / len(stocks)
    positive_ticker_ratio = sum(1 for stock in stocks if stock["change_pct"] > 0) / len(stocks)

    sorted_by_change = sorted(stocks, key=lambda item: item["change_pct"])
    leader = sorted_by_change[-1]["ticker"]
    laggard = sorted_by_change[0]["ticker"]

    momentum_strength = sum(abs(stock["change_pct"]) for stock in stocks) / len(stocks)

    leader_change = sorted_by_change[-1]["change_pct"]
    laggard_change = sorted_by_change[0]["change_pct"]
    leader_gap = leader_change - laggard_change

    volume_spike_ratio = sum(
        1 for stock in stocks if stock["volume"] > stock["avg_volume"] * 1.5
    ) / len(stocks)

    volatility_trend = (
        sum(1 for stock in stocks if stock["volatility"] > 5.0) / len(stocks)
    )

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
        "market_session": data.get("market_session", "unknown"),
        "qqq_change_pct": round(float(macro.get("qqq_change_pct", 0.0)), 3),
        "leader": leader,
        "laggard": laggard
    }
