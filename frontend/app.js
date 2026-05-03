const API_BASE = "http://127.0.0.1:8000";

let fullData = null;

async function loadPredictionData(endpoint = "/api/predict", method = "GET") {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers: { "Content-Type": "application/json" }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("Received data:", data); // Debug log
    fullData = data;
    renderAll(data);
    return data;
  } catch (error) {
    console.error("Failed to load data:", error);
    document.getElementById("explanationText").textContent = 
      "❌ Cannot connect to backend. Make sure python app.py is running on port 8000";
  }
}

function renderAll(data) {
  // Handle prediction (directly from data.prediction)
  if (data.prediction) {
    renderPrediction(data.prediction);
  }
  
  // Handle features (directly from data.features)
  if (data.features) {
    renderFeatures(data.features);
  }
  
  // Handle stock data (from data.data.stocks)
  if (data.data && data.data.stocks) {
    renderStocks(data.data.stocks);
  }
  
  // Handle news (from data.data.news)
  if (data.data && data.data.news) {
    renderNews(data.data.news);
  }
  
  // Handle explanation (directly from data.explanation)
  if (data.explanation) {
    document.getElementById("explanationText").innerHTML = `📝 ${data.explanation}`;
  }
  
  // Update timestamp
  if (data.data && data.data.last_updated) {
    const timestamp = document.getElementById("timestamp");
    if (timestamp) {
      const updateTime = new Date(data.data.last_updated).toLocaleString();
      timestamp.innerHTML = `Data from: ${updateTime} | Last refreshed: ${new Date().toLocaleTimeString()}`;
    }
  }
}

function renderPrediction(prediction) {
  console.log("Rendering prediction:", prediction);
  
  // Update prediction direction
  const directionElem = document.getElementById("predictionDirection");
  if (directionElem) {
    directionElem.textContent = prediction.predicted_direction;
    directionElem.className = `direction-value ${prediction.predicted_direction === "UP" ? "bullish" : "bearish"}`;
  }
  
  // Update confidence
  const confidenceElem = document.getElementById("confidenceValue");
  if (confidenceElem) {
    confidenceElem.textContent = `${prediction.confidence_pct}%`;
  }
  
  // Update expected move
  const moveElem = document.getElementById("expectedMoveValue");
  if (moveElem) {
    moveElem.textContent = `${prediction.expected_move_pct}%`;
  }
  
  // Update risk level
  const riskElem = document.getElementById("riskValue");
  if (riskElem) {
    riskElem.textContent = prediction.risk_level;
    // Color code risk level
    if (prediction.risk_level === "High") {
      riskElem.style.color = "#ef4444";
    } else if (prediction.risk_level === "Moderate") {
      riskElem.style.color = "#f59e0b";
    } else {
      riskElem.style.color = "#10b981";
    }
  }
  
  // Show model type and score
  const modelInfo = document.getElementById("modelInfo");
  if (modelInfo && prediction.model_type) {
    modelInfo.innerHTML = `🤖 Model: ${prediction.model_type} | Score: ${prediction.score} | Horizon: ${prediction.prediction_horizon}`;
  }
}

function renderFeatures(features) {
  const featureList = document.getElementById("featureList");
  if (!featureList) return;
  
  featureList.innerHTML = "";

  const labels = {
    basket_momentum: "📊 Basket Momentum",
    momentum_strength: "💪 Momentum Strength",
    leader_gap: "👑 Leader Gap",
    avg_relative_volume: "📈 Avg Relative Volume",
    volume_spike_ratio: "⚡ Volume Spike Ratio",
    avg_volatility: "🌊 Avg Volatility",
    volatility_trend: "📉 Volatility Trend",
    avg_news_sentiment: "📰 News Sentiment",
    positive_ticker_ratio: "✅ Positive Ticker Ratio",
    market_session: "🕒 Market Session",
    qqq_change_pct: "📊 QQQ Change %",
    agreement_strength: "🤝 Agreement Strength",
    leader: "🏆 Leader",
    laggard: "🐢 Laggard"
  };

  // Display key features first
  const keyFeatures = [
    "basket_momentum", "avg_relative_volume", "avg_news_sentiment",
    "positive_ticker_ratio", "leader", "laggard", "market_session"
  ];
  
  keyFeatures.forEach(key => {
    if (features[key] !== undefined && features[key] !== null) {
      const row = document.createElement("div");
      row.className = "feature-row";
      let value = features[key];
      let valueClass = "";
      
      if (typeof value === 'number') {
        value = value.toFixed(3);
        if (key === "basket_momentum") {
          valueClass = parseFloat(value) > 0 ? "positive" : parseFloat(value) < 0 ? "negative" : "";
        }
      }
      
      row.innerHTML = `
        <span class="feature-name">${labels[key] || key}</span>
        <span class="feature-value ${valueClass}">${value}</span>
      `;
      featureList.appendChild(row);
    }
  });
  
  // Add divider
  const divider = document.createElement("div");
  divider.className = "feature-divider";
  divider.innerHTML = "<hr style='margin: 10px 0; border-color: #e5e7eb;'>";
  featureList.appendChild(divider);
  
  // Display technical features
  const techFeatures = [
    "momentum_strength", "leader_gap", "volume_spike_ratio",
    "avg_volatility", "volatility_trend", "agreement_strength", "qqq_change_pct"
  ];
  
  techFeatures.forEach(key => {
    if (features[key] !== undefined && features[key] !== null) {
      const row = document.createElement("div");
      row.className = "feature-row";
      row.innerHTML = `
        <span class="feature-name">${labels[key] || key}</span>
        <span class="feature-value">${typeof features[key] === 'number' ? features[key].toFixed(3) : features[key]}</span>
      `;
      featureList.appendChild(row);
    }
  });
}

function renderStocks(stocks) {
  const tableBody = document.getElementById("stockTableBody");
  if (!tableBody) return;
  
  const searchValue = document.getElementById("searchBar") ? 
    document.getElementById("searchBar").value.toLowerCase() : "";

  tableBody.innerHTML = "";

  const filteredStocks = stocks.filter(stock => 
    stock.ticker.toLowerCase().includes(searchValue)
  );

  filteredStocks.forEach(stock => {
    const row = document.createElement("tr");
    const relVolume = stock.avg_volume ? (stock.volume / stock.avg_volume).toFixed(2) : "1.00";
    const changeClass = stock.change_pct >= 0 ? "positive" : "negative";
    const sentimentClass = stock.news_sentiment >= 0.6 ? "sentiment-positive" : 
                          stock.news_sentiment <= 0.4 ? "sentiment-negative" : "";
    
    row.innerHTML = `
      <td><strong>${stock.ticker}</strong></td>
      <td>$${typeof stock.price === 'number' ? stock.price.toFixed(2) : stock.price}</td>
      <td class="${changeClass}">${stock.change_pct >= 0 ? '+' : ''}${stock.change_pct}%</td>
      <td>${stock.volume.toLocaleString()}</td>
      <td>${relVolume}x</td>
      <td>${stock.volatility}%</td>
      <td class="${sentimentClass}">${stock.news_sentiment.toFixed(2)}</td>
    `;
    tableBody.appendChild(row);
  });
  
  // Update market summary
  const avgChange = stocks.reduce((sum, s) => sum + s.change_pct, 0) / stocks.length;
  const avgVolumeRatio = stocks.reduce((sum, s) => sum + (s.volume / s.avg_volume), 0) / stocks.length;
  const avgSentiment = stocks.reduce((sum, s) => sum + s.news_sentiment, 0) / stocks.length;
  
  const summaryDiv = document.getElementById("marketSummary");
  if (summaryDiv) {
    summaryDiv.innerHTML = `
      <div class="summary-item">📊 Avg Change: <strong class="${avgChange >= 0 ? 'positive' : 'negative'}">${avgChange >= 0 ? '+' : ''}${avgChange.toFixed(2)}%</strong></div>
      <div class="summary-item">📈 Avg Vol Ratio: <strong>${avgVolumeRatio.toFixed(2)}x</strong></div>
      <div class="summary-item">📰 Avg Sentiment: <strong>${avgSentiment.toFixed(2)}</strong></div>
    `;
  }
}

function renderNews(newsItems) {
  const newsList = document.getElementById("newsList");
  if (!newsList) return;
  
  newsList.innerHTML = "";

  if (!newsItems || newsItems.length === 0) {
    newsList.innerHTML = "<div class='news-item'>No recent news available</div>";
    return;
  }

  newsItems.forEach(item => {
    const block = document.createElement("div");
    block.className = "news-item";
    const sentimentIcon = item.sentiment >= 0.6 ? "🟢" : item.sentiment <= 0.4 ? "🔴" : "🟡";
    const impactClass = item.impact === "high" ? "impact-high" : item.impact === "medium" ? "impact-medium" : "impact-low";
    
    block.innerHTML = `
      <div class="news-title"><strong>${item.title}</strong></div>
      <div class="news-meta">
        ${sentimentIcon} ${item.ticker} • Sentiment: ${item.sentiment} • 
        Impact: <span class="${impactClass}">${item.impact}</span>
      </div>
    `;
    newsList.appendChild(block);
  });
}

async function refreshData() {
  const refreshBtn = document.getElementById("refreshBtn");
  if (refreshBtn) {
    refreshBtn.disabled = true;
    refreshBtn.textContent = "🔄 Refreshing...";
  }
  
  try {
    const response = await fetch(`${API_BASE}/api/refresh`, { 
      method: 'POST',
      headers: { "Content-Type": "application/json" }
    });
    const data = await response.json();
    console.log("Refresh response:", data);
    
    // Reload fresh data after refresh
    await loadPredictionData("/api/predict", "GET");
    
  } catch (error) {
    console.error("Refresh failed:", error);
    alert("Refresh failed. Check if backend is running.");
  } finally {
    if (refreshBtn) {
      refreshBtn.disabled = false;
      refreshBtn.textContent = "🔄 Refresh Data";
    }
  }
}

// Auto-refresh every 60 seconds
let autoRefreshInterval;

function startAutoRefresh() {
  if (autoRefreshInterval) clearInterval(autoRefreshInterval);
  autoRefreshInterval = setInterval(refreshData, 60000);
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  console.log("Frontend loaded, connecting to:", API_BASE);
  loadPredictionData();
  startAutoRefresh();
  
  // Add search handler
  const searchBar = document.getElementById("searchBar");
  if (searchBar) {
    searchBar.addEventListener("input", () => {
      if (fullData && fullData.data && fullData.data.stocks) {
        renderStocks(fullData.data.stocks);
      }
    });
  }
  
  // Add refresh button handler
  const refreshBtn = document.getElementById("refreshBtn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", refreshData);
  }
});