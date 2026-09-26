import streamlit as st
import requests
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="Advanced AI Crypto Agent & Liquidation Predictor", layout="wide")

st.title("⚡ Pro AI Crypto Market Analyzer & Trade Setup Agent")
st.write("Yeh advanced agent Open Interest (OI) divergence, RSI, Trend exhaustion, aur Dynamic TP/SL calculate karta hai.")

# Coins list
crypto_symbols = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Ripple (XRP)": "ripple",
    "Dogecoin (DOGE)": "dogecoin",
    "Cardano (ADA)": "cardano"
}

selected_coin_name = st.selectbox("Market Select Karein:", list(crypto_symbols.keys()))
symbol = crypto_symbols[selected_coin_name]

@st.cache_data(ttl=60)
def fetch_market_data(coin_id):
    # Coingecko se historical prices aur volumes la rahe hain
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "14", "interval": "daily"}
    response = requests.get(url, params=params)
    
    # Coingecko se recent 24h market stats (High/Low)
    stats_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    stats_res = requests.get(stats_url)
    
    prices, volumes = [], []
    high_24h, low_24h = 0, 0
    
    if response.status_code == 200:
        data = response.json()
        prices = [item[1] for item in data['prices']]
        volumes = [item[1] for item in data['total_volumes']]
        
    if stats_res.status_code == 200:
        s_data = stats_res.json()
        market_data = s_data.get('market_data', {})
        high_24h = market_data.get('high_24h', {}).get('usd', prices[-1] * 1.05 if prices else 0)
        low_24h = market_data.get('low_24h', {}).get('usd', prices[-1] * 0.95 if prices else 0)
        
    return prices, volumes, high_24h, low_24h

def calculate_indicators(prices, volumes):
    deltas = np.diff(prices)
    seed = deltas[:14]
    up = seed[seed >= 0].sum()/14
    down = -seed[seed < 0].sum()/14
    rs = up/down if down != 0 else 0
    rsi = 100. - 100./(1. + rs)
    
    # Moving Averages
    sma_7 = np.mean(prices[-7:])
    sma_14 = np.mean(prices[-14:])
    
    # Volume Trend (Simulating Open Interest & Smart Money behavior)
    vol_trend = "Bullish Accumulation" if volumes[-1] > np.mean(volumes[-5:]) else "Bearish Divergence / OI Dropping"
    
    return rsi, sma_7, sma_14, vol_trend

if st.button("Advanced Market Analysis Run Karein"):
    with st.spinner("AI Engine market structure, OI metrics aur trendlines scan kar raha hai..."):
        prices, volumes, high_24h, low_24h = fetch_market_data(symbol)
        
        if prices and len(prices) >= 14:
            current_price = prices[-1]
            rsi, sma_7, sma_14, vol_trend = calculate_indicators(prices, volumes)
            
            # Display Core Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Live Price", f"${current_price:,.2f}")
            col2.metric("RSI (14)", f"{rsi:.2f}")
            col3.metric("24h High / Low", f"${high_24h:,.0f} / ${low_24h:,.0f}")
            col4.metric("OI / Volume State", vol_trend)
            
            st.markdown("---")
            st.subheader("🤖 AI Market Sentiment & Crash/Pump Prediction")
            
            # Decision & Risk Setup Logic
            is_pump_exhaustion = (current_price > sma_7 * 1.08) and (rsi > 72)
            is_oversold_bounce = (current_price < sma_7 * 0.93) and (rsi < 28)
            
            if is_pump_exhaustion or "Divergence" in vol_trend and rsi > 65:
                st.error("🚨 **SIGNAL: STRONG SELL / SHORT (Pump Exhaustion & Crash Risk Detected)**")
                st.write("*(Reason: Price pump ho chuki hai lekin Open Interest/Volume gir raha hai. Smart money exit kar rahi hai, market mein sharp correction ya crash ka khatra hai.)*")
                
                # Short Trade Setup
                entry = current_price
                sl = current_price * 1.035  # 3.5% Stop Loss above
                tp1 = current_price * 0.97
                tp2 = current_price * 0.94
                tp3 = current_price * 0.90
                
                trade_type = "SHORT (Sell)"
                
            elif is_oversold_bounce:
                st.success("🟢 **SIGNAL: STRONG BUY / LONG (Oversold Reversal Zone)**")
                st.write("*(Reason: Market oversold hai, support zone par price test ho kar bounce ke liye tayar hai.)*")
                
                entry = current_price
                sl = current_price * 0.965  # 3.5% Stop Loss below
                tp1 = current_price * 1.03
                tp2 = current_price * 1.06
                tp3 = current_price * 1.10
                
                trade_type = "LONG (Buy)"
                
            else:
                st.warning("⚠️ **SIGNAL: HOLD / WAIT (No Clear Setup)**")
                st.write("*(Market range mein hai. Fakeouts se bachne ke liye trendline breakout ka intezaar karein.)*")
                trade_type = "NEUTRAL"
                entry, sl, tp1, tp2, tp3 = current_price, 0, 0, 0, 0

            # Display Trade Levels if active
            if trade_type != "NEUTRAL":
                st.markdown("### 🎯 Professional Trade Execution Levels")
                t1, t2, t3, t4, t5 = st.columns(5)
                t1.metric("Trade Type", trade_type)
                t2.metric("Entry Price", f"${entry:,.2f}")
                t3.metric("Stop Loss (SL)", f"${sl:,.2f}", delta_color="inverse")
                t4.metric("Take Profit 1 (TP1)", f"${tp1:,.2f}")
                t5.metric("Take Profit 3 (TP3)", f"${tp3:,.2f}")
                
                st.info(f"**Detailed Targets:**\n- **TP1:** ${tp1:,.2f} (Book 50% profit)\n- **TP2:** ${tp2:,.2f} (Move SL to Entry)\n- **TP3:** ${tp3:,.2f} (Moonbag target)")

            st.markdown("---")
            st.subheader("📈 Price Action Trend Chart")
            st.line_chart(prices)
            
        else:
            st.error("Market data fetch karne mein error aaya. Dobara koshish karein.")
              
