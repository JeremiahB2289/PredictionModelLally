"""Data ingestion layer for the starter project.

Tries live data first with yfinance. Falls back to local sample JSON.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_market_data.json"
TICKERS = ["QBTS", "QUBT", "IONQ", "RGTI"]

POSITIVE_WORDS = ["surge", "gain", "beat", "growth", "strong", "upgrade"]
NEGATIVE_WORDS = ["drop", "miss", "weak", "downgrade", "loss", "fall"]


def load_sample_data() -> Dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def _build_stock_record(ticker: str, info: Dict[str, Any]) -> Dict[str, Any]:
    price = float(info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)
    prev_close = float(info.get("previousClose") or price or 1.0)
    volume = int(info.get("volume") or 0)
    avg_volume = int(info.get("averageVolume") or max(volume, 1))

    if prev_close == 0:
        change_pct = 0.0
    else:
        change_pct = ((price - prev_close) / prev_close) * 100.0

    relative_volume = volume / avg_volume if avg_volume else 1.0
    volatility = abs(change_pct) * 1.2 + min(relative_volume, 4.0)

    headline = f"No live headline yet for {ticker}."
    sentiment = 0.5
    text = headline.lower()
    for word in POSITIVE_WORDS:
        if word in text:
            sentiment += 0.1
    for word in NEGATIVE_WORDS:
        if word in text:
            sentiment -= 0.1
    sentiment = max(0.0, min(1.0, sentiment))

    return {
        "ticker": ticker,
        "price": round(price, 2),
        "change_pct": round(change_pct, 2),
        "volume": volume,
        "avg_volume": avg_volume,
        "volatility": round(volatility, 2),
        "news_sentiment": round(sentiment, 2),
        "news_count": 0,
        "headline": f"No live headline yet for {ticker}."
    }


def try_live_pull() -> Dict[str, Any]:
    try:
        import yfinance as yf
    except Exception as exc:
        raise RuntimeError("yfinance is not installed.") from exc

    stock_rows: List[Dict[str, Any]] = []

    for ticker in TICKERS:
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            stock_rows.append(_build_stock_record(ticker, info))
        except Exception:
            continue

    if not stock_rows:
        raise RuntimeError("Could not fetch live market data.")

    live_data = load_sample_data()
    live_data["last_updated"] = datetime.utcnow().isoformat()
    live_data["stocks"] = stock_rows
    live_data["market_session"] = "regular"
    return live_data


def refresh_data() -> Dict[str, Any]:
    try:
        fresh = try_live_pull()
        save_data(fresh)
        return fresh
    except Exception:
        return load_sample_data()
