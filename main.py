import streamlit as st
import pandas as pd
from binance.client import Client
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator, StochRSIIndicator
import time
import os

# Binance API (можно оставить пустыми для публичных данных)
client = Client(api_key=os.getenv("BINANCE_API_KEY", ""), api_secret=os.getenv("BINANCE_API_SECRET", ""))

PAIRS = {
    "BTCUSDT": "BTC/USDT",
    "ETHUSDT": "ETH/USDT",
    "SOLUSDT": "SOL/USDT",
    "PAXGUSDT": "PAXG/USDT"
}

def fetch_ohlcv(symbol: str, interval="1h", limit=150):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        if not klines or len(klines) < 100:
            return None
        df = pd.DataFrame(klines, columns=[
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base", "Taker buy quote", "Ignore"
        ])
        df["Close"] = pd.to_numeric(df["Close"])
        return df
    except Exception as e:
        print(f"Ошибка при получении данных для {symbol}: {e}")
        return None

def analyze(df):
    if df is None or df.empty or len(df) < 100:
        return ["❌ Недостаточно данных"]

    df["EMA50"] = EMAIndicator(close=df["Close"], window=50).ema_indicator()
    df["RSI"] = RSIIndicator(close=df["Close"]).rsi()
    df["StochRSI"] = StochRSIIndicator(close=df["Close"]).stochrsi()

    last = df.iloc[-1]
    signal = []

    if last["RSI"] < 30:
        signal.append("🟢 RSI перепродан")
    elif last["RSI"] > 70:
        signal.append("🔴 RSI перекуплен")

    if last["Close"] > last["EMA50"]:
        signal.append("📈 Цена выше EMA50 (бычий тренд)")
    else:
        signal.append("📉 Цена ниже EMA50 (медвежий тренд)")

    if last["StochRSI"] < 0.2:
        signal.append("🟢 StochRSI перепродан")
    elif last["StochRSI"] > 0.8:
        signal.append("🔴 StochRSI перекуплен")

    return signal if signal else ["⚪ Сигналов нет"]

# Streamlit UI
st.set_page_config(page_title="Крипто-сигналы (Binance)", layout="centered")

st.title("📈 Крипто-сигналы (Binance)")
st.subheader("Получай простые технические сигналы по ключевым парам.")
st.markdown("---")

for symbol, display_name in PAIRS.items():
    df = fetch_ohlcv(symbol)
    signals = analyze(df)

    st.markdown(f"### {display_name}")
    for s in signals:
        st.write(s)
    st.markdown("---")

# Обновление по кнопке
if st.button("🔄 Обновить"):
    st.rerun()
