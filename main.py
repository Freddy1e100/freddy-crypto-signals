import streamlit as st
import pandas as pd
import ta
import ccxt
import os
import requests
from datetime import datetime, timedelta

# Настройки
st.set_page_config(page_title="📈 Крипто-сигналы (Binance)", layout="centered")
st.title("📈 Крипто-сигналы (Binance)")
st.write("Получай простые технические сигналы по ключевым парам.")

# Telegram данные
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or "7903391510:AAFgkj03oD8CGL3hfVNKPAE64phffpsxAEM"
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID") or 646839309)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except Exception as e:
        print("❌ Ошибка Telegram:", e)

# Binance
exchange = ccxt.binance()

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "PAXG/USDT"]

def fetch_data(pair):
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        return df
    except Exception as e:
        print(f"Ошибка получения данных для {pair}: {e}")
        return pd.DataFrame()

def analyze(df):
    if df.empty or len(df) < 50:
        return None

    df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50).ema_indicator()
    df["RSI"] = ta.momentum.rsi(df["Close"])
    df["StochRSI"] = ta.momentum.stochrsi(df["Close"])

    last = df.iloc[-1]
    signals = []

    if last["RSI"] < 30:
        signals.append("🟢 RSI перепродан")
    elif last["RSI"] > 70:
        signals.append("🔴 RSI перекуплен")

    if last["Close"] > last["EMA50"]:
        signals.append("📈 Цена выше EMA50 (тренд вверх)")
    else:
        signals.append("📉 Цена ниже EMA50 (тренд вниз)")

    if last["StochRSI"] < 0.2:
        signals.append("🟢 StochRSI перепродан")
    elif last["StochRSI"] > 0.8:
        signals.append("🔴 StochRSI перекуплен")

    return signals if signals else ["ℹ️ Сигналов нет"]

# Отображение
all_signals = []
for pair in PAIRS:
    df = fetch_data(pair)
    analysis = analyze(df)

    st.subheader(pair)
    if not analysis:
        st.error("❌ Недостаточно данных")
        all_signals.append(f"{pair}:\n❌ Недостаточно данных")
    else:
        for s in analysis:
            st.write(s)
        all_signals.append(f"{pair}:\n" + "\n".join(analysis))

# Кнопка отправки в Telegram
if st.button("📲 Отправить сигналы в Telegram"):
    for signal in all_signals:
        if "🟢" in signal or "🔴" in signal:
            send_telegram_message(signal)
    st.success("Сигналы отправлены!")
