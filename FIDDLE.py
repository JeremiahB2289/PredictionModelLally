"""
Quantum Stock Tracker — Live Dashboard
Tracks QBTS, IONQ, RGTI, QUBT with real-time data via yfinance.
Auto-refreshes every 30 seconds. Blue/white theme with Plotly charts.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum Stock Tracker",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Tickers & Config ─────────────────────────────────────────────────────────
TICKERS = ["QBTS", "IONQ", "RGTI", "QUBT"]

TICKER_NAMES = {
    "QBTS": "D-Wave Quantum",
    "IONQ": "IonQ",
    "RGTI": "Rigetti Computing",
    "QUBT": "Quantum Computing Inc.",
}

# Color palette for each ticker
TICKER_COLORS = {
    "QBTS": "#1565C0",   # deep blue
    "IONQ": "#0288D1",   # sky blue
    "RGTI": "#26C6DA",   # cyan
    "QUBT": "#42A5F5",   # light blue
}

TIMEFRAMES = {
    "1D": ("1d",  "5m"),
    "1W": ("5d",  "30m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
}

REFRESH_INTERVAL = 30  # seconds

# ─── Custom CSS ───────────────────────────────────────────────────────────────
def inject_css(dark_mode: bool):
    if dark_mode:
        bg        = "#0A1628"
        card_bg   = "#0F2040"
        surface   = "#162B50"
        text      = "#E8F0FE"
        subtext   = "#90A4AE"
        border    = "#1E3A5F"
        accent    = "#1565C0"
    else:
        bg        = "#F0F4FF"
        card_bg   = "#FFFFFF"
        surface   = "#E8EEF9"
        text      = "#0D1B3E"
        subtext   = "#546E8C"
        border    = "#C5D5F0"
        accent    = "#1565C0"

    st.markdown(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

      :root {{
        --bg: {bg};
        --card: {card_bg};
        --surface: {surface};
        --text: {text};
        --sub: {subtext};
        --border: {border};
        --accent: {accent};
      }}

      .stApp {{ background: var(--bg) !important; }}
      .block-container {{ padding: 1.5rem 2rem !important; max-width: 100% !important; }}

      /* Header */
      .dash-header {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 0 1.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
      }}
      .dash-title {{
        font-family: 'Inter', sans-serif; font-weight: 700;
        font-size: 1.6rem; color: var(--text); letter-spacing: -0.03em;
      }}
      .dash-subtitle {{
        font-family: 'Inter', sans-serif; font-size: 0.8rem;
        color: var(--sub); margin-top: 2px;
      }}
      .live-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(21,101,192,0.15); border: 1px solid rgba(21,101,192,0.3);
        padding: 4px 12px; border-radius: 20px;
        font-family: 'Inter', sans-serif; font-size: 0.75rem; color: #42A5F5;
        font-weight: 600; letter-spacing: 0.05em;
      }}
      .live-dot {{
        width: 7px; height: 7px; border-radius: 50%;
        background: #42A5F5; animation: pulse 1.5s infinite;
      }}
      @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.5; transform: scale(0.8); }}
      }}

      /* Stock Cards */
      .stock-card {{
        background: var(--card); border: 1px solid var(--border);
        border-radius: 12px; padding: 1.25rem 1.4rem;
        margin-bottom: 0.5rem;
        transition: box-shadow 0.2s ease;
      }}
      .stock-card:hover {{ box-shadow: 0 4px 24px rgba(21,101,192,0.12); }}

      .card-ticker {{
        font-family: 'JetBrains Mono', monospace; font-weight: 600;
        font-size: 1rem; color: var(--accent); letter-spacing: 0.05em;
      }}
      .card-name {{
        font-family: 'Inter', sans-serif; font-size: 0.72rem;
        color: var(--sub); margin-top: 2px;
      }}
      .card-price {{
        font-family: 'JetBrains Mono', monospace; font-weight: 600;
        font-size: 1.6rem; color: var(--text); margin-top: 0.5rem;
        letter-spacing: -0.02em;
      }}
      .card-change-up {{
        font-family: 'Inter', sans-serif; font-weight: 600;
        font-size: 0.88rem; color: #00C853;
      }}
      .card-change-down {{
        font-family: 'Inter', sans-serif; font-weight: 600;
        font-size: 0.88rem; color: #F44336;
      }}
      .card-meta {{
        font-family: 'Inter', sans-serif; font-size: 0.72rem;
        color: var(--sub); margin-top: 6px;
        display: flex; gap: 12px;
      }}
      .card-meta span {{ color: var(--text); font-weight: 500; }}

      /* Section Headers */
      .section-label {{
        font-family: 'Inter', sans-serif; font-size: 0.7rem;
        font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
        color: var(--sub); margin-bottom: 0.75rem; margin-top: 1.5rem;
      }}

      /* Timeframe buttons */
      div[data-testid="stHorizontalBlock"] .stButton button {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--sub) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important; font-weight: 500 !important;
        border-radius: 6px !important; padding: 4px 14px !important;
        transition: all 0.15s !important;
      }}
      div[data-testid="stHorizontalBlock"] .stButton button:hover {{
        background: var(--accent) !important;
        color: #fff !important; border-color: var(--accent) !important;
      }}

      /* Selectbox / general widgets */
      .stSelectbox label, .stSlider label {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important; color: var(--sub) !important;
      }}

      /* Hide Streamlit chrome */
      #MainMenu, footer, header {{ visibility: hidden; }}
      .stDeployButton {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)


# ─── Data Fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=28)
def fetch_quote(ticker: str) -> dict:
    """Fetch current price, change, volume, hi/lo for a ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="2d", interval="1d")

        if hist.empty or len(hist) < 1:
            return {}

        current  = float(info.last_price) if hasattr(info, "last_price") and info.last_price else float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else float(hist["Close"].iloc[-1])
        change   = current - prev_close
        pct      = (change / prev_close) * 100

        return {
            "price":      current,
            "change":     change,
            "pct":        pct,
            "prev_close": prev_close,
            "volume":     int(info.three_month_average_volume) if hasattr(info, "three_month_average_volume") and info.three_month_average_volume else 0,
            "high":       float(info.year_high) if hasattr(info, "year_high") and info.year_high else current,
            "low":        float(info.year_low)  if hasattr(info, "year_low")  and info.year_low  else current,
        }
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")
        return {}


@st.cache_data(ttl=55)
def fetch_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Fetch OHLCV history for charting."""
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()


# ─── Chart Builders ────────────────────────────────────────────────────────────
def price_chart(ticker: str, period: str, interval: str,
                show_ma: bool, show_volume: bool, dark_mode: bool) -> go.Figure:
    """Candlestick + optional MAs + optional volume for a single ticker."""
    df = fetch_history(ticker, period, interval)
    if df.empty:
        return go.Figure()

    bg_color  = "#0F2040" if dark_mode else "#FFFFFF"
    grid_color = "rgba(255,255,255,0.05)" if dark_mode else "rgba(0,0,0,0.06)"
    text_color = "#90A4AE" if dark_mode else "#546E8C"
    color      = TICKER_COLORS[ticker]

    rows   = 2 if show_volume else 1
    heights= [0.72, 0.28] if show_volume else [1]

    from plotly.subplots import make_subplots
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=heights)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#00C853", decreasing_line_color="#F44336",
        increasing_fillcolor="#00C853",  decreasing_fillcolor="#F44336",
        name=ticker, showlegend=False,
    ), row=1, col=1)

    # Moving averages
    if show_ma and len(df) >= 20:
        ma20 = df["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma20, name="MA 20",
            line=dict(color="#FFB300", width=1.2, dash="solid"),
        ), row=1, col=1)

    if show_ma and len(df) >= 50:
        ma50 = df["Close"].rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma50, name="MA 50",
            line=dict(color="#AB47BC", width=1.2, dash="dot"),
        ), row=1, col=1)

    # Volume bars
    if show_volume:
        vol_colors = [
            "#00C853" if c >= o else "#F44336"
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"], name="Volume",
            marker_color=vol_colors, opacity=0.6, showlegend=False,
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor=bg_color, plot_bgcolor=bg_color,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_rangeslider_visible=False,
        legend=dict(
            font=dict(family="Inter", size=11, color=text_color),
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            orientation="h", x=0, y=1.05,
        ),
        font=dict(family="Inter", color=text_color),
        hovermode="x unified",
    )
    fig.update_xaxes(
        showgrid=True, gridcolor=grid_color,
        zeroline=False, tickfont=dict(size=10),
        showspikes=True, spikecolor=color,
        spikethickness=1, spikedash="dot",
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=grid_color,
        zeroline=False, tickfont=dict(size=10),
        tickprefix="$",
    )
    return fig


def comparison_chart(period: str, interval: str, dark_mode: bool) -> go.Figure:
    """Normalized line chart comparing all four tickers."""
    bg_color   = "#0F2040" if dark_mode else "#FFFFFF"
    grid_color = "rgba(255,255,255,0.05)" if dark_mode else "rgba(0,0,0,0.06)"
    text_color = "#90A4AE" if dark_mode else "#546E8C"

    fig = go.Figure()
    for ticker in TICKERS:
        df = fetch_history(ticker, period, interval)
        if df.empty:
            continue
        base = df["Close"].iloc[0]
        pct  = ((df["Close"] - base) / base) * 100

        fig.add_trace(go.Scatter(
            x=df.index, y=pct, name=ticker,
            line=dict(color=TICKER_COLORS[ticker], width=2),
            hovertemplate=f"<b>{ticker}</b><br>%{{y:.2f}}%<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot", line_color="rgba(150,150,150,0.4)", line_width=1)

    fig.update_layout(
        paper_bgcolor=bg_color, plot_bgcolor=bg_color,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            font=dict(family="Inter", size=12, color=text_color),
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            orientation="h", x=0, y=1.06,
        ),
        font=dict(family="Inter", color=text_color),
        hovermode="x unified",
        yaxis_ticksuffix="%",
    )
    fig.update_xaxes(showgrid=True, gridcolor=grid_color, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor=grid_color, zeroline=False, tickfont=dict(size=10))
    return fig


# ─── Stock Card HTML ────────────────────────────────────────────────────────────
def stock_card_html(ticker: str, data: dict) -> str:
    if not data:
        return f"""
        <div class="stock-card">
          <div class="card-ticker">{ticker}</div>
          <div class="card-name">{TICKER_NAMES[ticker]}</div>
          <div class="card-price" style="font-size:1rem;color:#F44336;">Data unavailable</div>
        </div>"""

    price   = data["price"]
    pct     = data["pct"]
    change  = data["change"]
    arrow   = "▲" if pct >= 0 else "▼"
    cls     = "card-change-up" if pct >= 0 else "card-change-down"
    vol_fmt = f"{data['volume']:,}" if data["volume"] else "N/A"
    dot_color = TICKER_COLORS[ticker]

    return f"""
    <div class="stock-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div class="card-ticker" style="color:{dot_color};">{ticker}</div>
          <div class="card-name">{TICKER_NAMES[ticker]}</div>
        </div>
        <div style="text-align:right;">
          <div class="card-price">${price:.2f}</div>
          <div class="{cls}">{arrow} {abs(change):.2f} ({abs(pct):.2f}%)</div>
        </div>
      </div>
      <div class="card-meta">
        <div>52W H: <span>${data['high']:.2f}</span></div>
        <div>52W L: <span>${data['low']:.2f}</span></div>
        <div>Avg Vol: <span>{vol_fmt}</span></div>
      </div>
    </div>"""


# ─── Main App ──────────────────────────────────────────────────────────────────
def main():
    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        dark_mode  = st.toggle("Dark Mode", value=True)
        show_ma    = st.toggle("Moving Averages (20/50)", value=True)
        show_vol   = st.toggle("Volume Bars", value=True)
        st.divider()
        st.markdown("**Auto-refresh**")
        st.markdown(f"Every **{REFRESH_INTERVAL}s**")
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        st.divider()
        st.markdown("**Tracked Tickers**")
        for t in TICKERS:
            st.markdown(
                f'<span style="font-family:monospace;color:{TICKER_COLORS[t]};font-weight:600;">'
                f'{t}</span> — {TICKER_NAMES[t]}',
                unsafe_allow_html=True,
            )

    inject_css(dark_mode)

    # ── Header ──
    now_str = datetime.now().strftime("%b %d, %Y  %H:%M:%S")
    st.markdown(f"""
    <div class="dash-header">
      <div>
        <div class="dash-title">⚛️ Quantum Stock Tracker</div>
        <div class="dash-subtitle">QBTS · IONQ · RGTI · QUBT — Quantum Computing Sector</div>
      </div>
      <div style="text-align:right;">
        <div class="live-badge"><div class="live-dot"></div>LIVE</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.72rem;
                    color:{'#90A4AE' if dark_mode else '#546E8C'};margin-top:6px;">
          Updated: {now_str}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch all quotes ──
    quotes = {t: fetch_quote(t) for t in TICKERS}

    # ── Stock Cards Row ──
    st.markdown('<div class="section-label">Market Overview</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, ticker in enumerate(TICKERS):
        with cols[i]:
            st.markdown(stock_card_html(ticker, quotes[ticker]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Timeframe selector ──
    st.markdown('<div class="section-label">Individual Charts</div>', unsafe_allow_html=True)
    tf_cols = st.columns([1,1,1,1,8])
    selected_tf = st.session_state.get("tf", "1M")
    for i, tf_label in enumerate(TIMEFRAMES.keys()):
        with tf_cols[i]:
            if st.button(tf_label, key=f"tf_{tf_label}"):
                st.session_state["tf"] = tf_label
                selected_tf = tf_label

    period, interval = TIMEFRAMES[selected_tf]

    # ── Individual price charts (2×2 grid) ──
    row1 = st.columns(2)
    row2 = st.columns(2)
    chart_cols = [row1[0], row1[1], row2[0], row2[1]]

    for i, ticker in enumerate(TICKERS):
        with chart_cols[i]:
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-weight:600;'
                f'font-size:0.9rem;color:{TICKER_COLORS[ticker]};margin-bottom:4px;">'
                f'{ticker} — {TICKER_NAMES[ticker]}</div>',
                unsafe_allow_html=True,
            )
            fig = price_chart(ticker, period, interval, show_ma, show_vol, dark_mode)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Combined Comparison Chart ──
    st.markdown('<div class="section-label">Sector Comparison (% Change)</div>', unsafe_allow_html=True)
    comp_fig = comparison_chart(period, interval, dark_mode)
    st.plotly_chart(comp_fig, use_container_width=True, config={"displayModeBar": False})

    # ── Footer / Auto-refresh ──
    st.markdown(
        f'<div style="text-align:center;font-family:Inter,sans-serif;font-size:0.72rem;'
        f'color:{"#546E8C" if not dark_mode else "#37474F"};margin-top:2rem;padding-top:1rem;'
        f'border-top:1px solid {"#C5D5F0" if not dark_mode else "#1E3A5F"};">'
        f'Data via yfinance · Refreshes every {REFRESH_INTERVAL}s · '
        f'For informational purposes only, not financial advice.</div>',
        unsafe_allow_html=True,
    )

    # Auto-refresh
    time.sleep(REFRESH_INTERVAL)
    st.rerun()


if __name__ == "__main__":
    main()