const API_BASE = "http://127.0.0.1:8000";

let fullPayload = null;

async function loadPredictionData(endpoint = "/api/predict", method = "GET") {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers: { "Content-Type": "application/json" }
    });
    const data = await response.json();
    fullPayload = data;
    renderAll(data);
  } catch (error) {
    console.error("Failed to load data:", error);
    document.getElementById("explanationText").textContent =
      "Could not connect to the backend. Start the API server first.";
  }
}

function renderAll(payload) {
  renderPrediction(payload.prediction);
  renderFeatures(payload.features);
  renderStocks(payload.data.stocks);
  renderNews(payload.data.news);
  document.getElementById("explanationText").textContent = payload.explanation;
}

function renderPrediction(prediction) {
  document.getElementById("predictionDirection").textContent = prediction.predicted_direction;
  document.getElementById("confidenceValue").textContent = `${prediction.confidence_pct}%`;
  document.getElementById("expectedMoveValue").textContent = `${prediction.expected_move_pct}%`;
  document.getElementById("riskValue").textContent = prediction.risk_level;
}

function renderFeatures(features) {
  const featureList = document.getElementById("featureList");
  featureList.innerHTML = "";

  const labels = {
    basket_momentum: "Basket Momentum",
    avg_relative_volume: "Avg Relative Volume",
    avg_volatility: "Avg Volatility",
    avg_news_sentiment: "Avg News Sentiment",
    positive_ticker_ratio: "Positive Ticker Ratio",
    market_session: "Market Session",
    qqq_change_pct: "QQQ Change %",
    leader: "Leader",
    laggard: "Laggard"
  };

  Object.entries(features).forEach(([key, value]) => {
    const row = document.createElement("div");
    row.className = "feature-row";
    row.innerHTML = `<span>${labels[key] || key}</span><strong>${value}</strong>`;
    featureList.appendChild(row);
  });
}

function renderStocks(stocks) {
  const tableBody = document.getElementById("stockTableBody");
  const searchValue = document.getElementById("searchBar").value.toLowerCase();

  tableBody.innerHTML = "";

  stocks
    .filter(stock => stock.ticker.toLowerCase().includes(searchValue))
    .forEach(stock => {
      const row = document.createElement("tr");
      const relVolume = stock.avg_volume ? (stock.volume / stock.avg_volume).toFixed(2) : "1.00";
      const changeClass = stock.change_pct >= 0 ? "positive" : "negative";
      row.innerHTML = `
        <td>${stock.ticker}</td>
        <td>$${stock.price}</td>
        <td class="${changeClass}">${stock.change_pct}%</td>
        <td>${stock.volume.toLocaleString()}</td>
        <td>${relVolume}</td>
        <td>${stock.volatility}</td>
        <td>${stock.news_sentiment}</td>
      `;
      tableBody.appendChild(row);
    });
}

function renderNews(newsItems) {
  const newsList = document.getElementById("newsList");
  newsList.innerHTML = "";

  newsItems.forEach(item => {
    const block = document.createElement("div");
    block.className = "news-item";
    block.innerHTML = `
      <strong>${item.title}</strong>
      <div class="news-meta">${item.ticker} • Sentiment: ${item.sentiment} • Impact: ${item.impact}</div>
    `;
    newsList.appendChild(block);
  });
}

document.getElementById("refreshBtn").addEventListener("click", async () => {
  await loadPredictionData("/api/refresh", "POST");
});

document.getElementById("searchBar").addEventListener("input", () => {
  if (fullPayload) {
    renderStocks(fullPayload.data.stocks);
  }
});

loadPredictionData();
