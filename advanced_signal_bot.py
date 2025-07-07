import os
from dotenv import load_dotenv
import requests
import pandas as pd
import numpy as np
import datetime
import asyncio
import telegram

# —————— 0) .env DOSYASINI YÜKLE ——————
load_dotenv()

# —————— DEBUG (doğru okuyup okumadığını kontrol et) ——————
print("📣 Çalışma dizini:", os.getcwd())
print("📣 Dosyalar:", os.listdir())
print("📣 TOKEN env’den:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("📣 CHAT_ID env’den:", os.getenv("TELEGRAM_CHAT_ID"))
print("📣 ETHERSCAN_API_KEY env’den:", os.getenv("ETHERSCAN_API_KEY"))

# —————— 1) AYARLAR ——————
TOKEN             = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID           = int(os.getenv("TELEGRAM_CHAT_ID") or 0)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

bot = telegram.Bot(token=TOKEN)

symbols    = ["BTCUSDT", "ETHUSDT", "PEPEUSDT"]
timeframes = ["15m", "1h", "4h", "1d"]

# —————— 2) VERİ İNDİRME & GÖSTERGELER ——————

def fetch_ohlc_binance(symbol, interval="30m", limit=500):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()
    df = pd.DataFrame(data, columns=[
        "Open Time","Open","High","Low","Close","Volume",
        "Close Time","Quote Asset Volume","Number of Trades",
        "Taker Buy Base","Taker Buy Quote","Ignore"
    ])
    df[["High","Low","Close","Volume"]] = df[["High","Low","Close","Volume"]].astype(float)
    df["Time"] = pd.to_datetime(df["Close Time"], unit="ms")
    return df

def compute_atr(df, period=14):
    high, low = df["High"], df["Low"]
    prev_close = df["Close"].shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().iloc[-1]

def compute_rsi(series, period=14):
    delta = series.diff()
    gain  = np.where(delta > 0, delta, 0)
    loss  = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).iloc[-1]

def compute_macd_histogram(series):
    ema12  = series.ewm(span=12, adjust=False).mean()
    ema26  = series.ewm(span=26, adjust=False).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return (macd - signal).iloc[-1]

def compute_ema_ribbon(series):
    spans = [20,25,30,35,40,45,50,55]
    emas = [series.ewm(span=s, adjust=False).mean().iloc[-1] for s in spans]
    if all(emas[i] > emas[i+1] for i in range(len(emas)-1)): return "Bullish"
    if all(emas[i] < emas[i+1] for i in range(len(emas)-1)): return "Bearish"
    return "Neutral"

def check_volume_spike(df):
    avg_vol = df["Volume"].iloc[-11:-1].mean()
    return df["Volume"].iloc[-1] > avg_vol * 1.2

# —————— 3) SİNYAL ANALİZLERİ ——————

def analyze_single_timeframe(symbol, interval):
    try:
        df    = fetch_ohlc_binance(symbol, interval)
        price = df["Close"].iloc[-1]
        atr   = compute_atr(df)
        rsi   = compute_rsi(df["Close"])
        macd  = compute_macd_histogram(df["Close"])
        ribbon= compute_ema_ribbon(df["Close"])
        spike = check_volume_spike(df)

        bullish = sum([
            atr >= price * 0.003,
            rsi > 50,
            macd > 0,
            ribbon == "Bullish",
            spike
        ])
        bearish = sum([
            atr < price * 0.003,
            rsi < 50,
            macd < 0,
            ribbon == "Bearish",
            not spike
        ])

        if bullish >= 3:    sig = "🟢 AL"
        elif bearish >= 3:  sig = "🔴 SAT"
        else:               sig = "🟡 BEKLE"

        detail = (
            f"{sig}\n"
            f"    Price={price:.8f}\n"
            f"    ATR={atr:.5f}\n"
            f"    RSI={rsi:.1f}"
            + ("\n    📈 Hacim Spike!" if spike else "")
        )
        return detail

    except Exception as e:
        return f"❗️ Hata: {e}"

def analyze_multi_timeframes(symbol):
    lines = [f"🔹 {symbol}"]
    for tf in timeframes:
        lines.append(f"  {tf}: {analyze_single_timeframe(symbol, tf)}")

    signals = [analyze_single_timeframe(symbol, tf) for tf in timeframes]
    if   all("AL" in s for s in signals):    final = "**🟢 GÜÇLÜ AL**"
    elif all("SAT" in s for s in signals):   final = "**🔴 GÜÇLÜ SAT**"
    else:                                    final = "**🟡 BEKLE**"
    lines.append(f"→ {final}")

    return "\n".join(lines)

# —————— 4) TELEGRAM’A GÖNDERİM ——————

async def send_signals():
    now  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    text = f"📊 MULTI-TIMEFRAME SİNYALLER - {now}\n\n"
    for sym in symbols:
        text += analyze_multi_timeframes(sym) + "\n\n"
    await bot.send_message(chat_id=CHAT_ID, text=text)

# —————— 5) ANA DÖNGÜ ——————

async def run_loop():
    print("Bot çalışıyor… Her 30 dakikada sinyaller gönderilecek.")
    while True:
        await send_signals()
        await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(run_loop())
