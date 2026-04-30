import requests
import csv
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()
import os

API_KEY = os.getenv("MASSIVE_API_KEY")

if not API_KEY:
    raise ValueError("Missing MASSIVE_API_KEY environment variable")

TICKERS = ["QBTS", "QUBT", "IONQ", "RGTI"]
BASE_URL = "https://api.massive.com/v2/aggs/ticker/{}/range/1/minute/{}/{}"

START_DATE = "2025-04-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")

OUTPUT_FILE = "../../data/training_data.csv"


# ---------------------------
# Fetch data from Massive
# ---------------------------
def fetch_data(ticker):
    url = BASE_URL.format(ticker, START_DATE, END_DATE)
    params = {"apiKey": API_KEY}

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        print(f"Error fetching {ticker}")
        return []

    return data["results"]


# ---------------------------
# Build time-aligned dataset
# ---------------------------
def align_data(all_data):
    time_map = defaultdict(dict)

    for ticker, candles in all_data.items():
        for c in candles:
            timestamp = c["t"]
            time_map[timestamp][ticker] = c

    aligned = []
    for t in sorted(time_map.keys()):
        if len(time_map[t]) == len(TICKERS):
            aligned.append((t, time_map[t]))

    return aligned


# ---------------------------
# Feature builder
# ---------------------------
def build_features(snapshot):
    stocks = []

    for ticker, c in snapshot.items():
        open_p = c["o"]
        close = c["c"]
        high = c["h"]
        low = c["l"]
        volume = c["v"]

        change_pct = ((close - open_p) / open_p) * 100
        volatility = ((high - low) / open_p) * 100

        stocks.append({
            "change_pct": change_pct,
            "volume": volume,
            "avg_volume": volume,  # simple placeholder
            "volatility": volatility
        })

    n = len(stocks)

    basket_momentum = sum(s["change_pct"] for s in stocks) / n
    momentum_strength = sum(abs(s["change_pct"]) for s in stocks) / n

    avg_relative_volume = 1.0  # placeholder for now

    avg_volatility = sum(s["volatility"] for s in stocks) / n
    volatility_trend = sum(1 for s in stocks if s["volatility"] > 2.0) / n

    positive_ratio = sum(1 for s in stocks if s["change_pct"] > 0) / n
    agreement_strength = abs(positive_ratio - 0.5) * 2

    sorted_changes = sorted(s["change_pct"] for s in stocks)
    leader_gap = sorted_changes[-1] - sorted_changes[0]

    return [
        basket_momentum,
        momentum_strength,
        avg_relative_volume,
        avg_volatility,
        volatility_trend,
        positive_ratio,
        agreement_strength,
        leader_gap
    ]


# ---------------------------
# Build dataset
# ---------------------------
def build_dataset():
    print("Fetching data...")
    all_data = {ticker: fetch_data(ticker) for ticker in TICKERS}

    print("Aligning timestamps...")
    aligned = align_data(all_data)

    print(f"Total aligned points: {len(aligned)}")

    rows = []

    for i in range(len(aligned) - 15):
        t, snapshot = aligned[i]
        future_t, future_snapshot = aligned[i + 15]

        features = build_features(snapshot)

        # sector price = avg close
        current_price = sum(snapshot[t]["c"] for t in snapshot) / len(snapshot)
        future_price = sum(future_snapshot[t]["c"] for t in future_snapshot) / len(future_snapshot)

        label = 1 if future_price > current_price else 0

        rows.append(features + [label])

    print(f"Saving {len(rows)} rows...")

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "basket_momentum",
            "momentum_strength",
            "avg_relative_volume",
            "avg_volatility",
            "volatility_trend",
            "positive_ticker_ratio",
            "agreement_strength",
            "leader_gap",
            "label"
        ])

        writer.writerows(rows)

    print("Done!")


if __name__ == "__main__":
    build_dataset()