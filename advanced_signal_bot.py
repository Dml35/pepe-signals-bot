#!/usr/bin/env python3
import os
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# ——————————————
# 1) ENV’leri oku & temizle
TOKEN        = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID_RAW  = os.getenv("TELEGRAM_CHAT_ID", "").strip()
PEPE_LEVEL   = os.getenv("PEPE_ALERT_LEVEL", "0").strip()

# 2) CHAT_ID’i güvenli parse et
if CHAT_ID_RAW.isdigit():
    CHAT_ID = int(CHAT_ID_RAW)
else:
    CHAT_ID = None

# 3) Eşik değerini float’a çevir
try:
    THRESHOLD = float(PEPE_LEVEL)
except:
    THRESHOLD = 0.0

bot = Bot(token=TOKEN)

def get_pepe_price() -> float | None:
    url = "https://api.binance.com/api/v3/ticker/price"
    try:
        r = requests.get(url, params={"symbol": "PEPEUSDT"}, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("❗️ API isteği hatası:", e)
        return None

    price_str = data.get("price")
    if price_str is None:
        print("❗️ 'price' alanı yok, dönen veri:", data)
        return None

    try:
        return float(price_str)
    except:
        print("❗️ 'price' float’a çevrilemedi:", price_str)
        return None

def send_signals():
    price = get_pepe_price()
    if price is None:
        return

    print(f"📊 PEPE fiyatı: {price:.8f} USDT — Eşik = {THRESHOLD:.8f}")
    if CHAT_ID and price <= THRESHOLD:
        try:
            bot.send_message(
                chat_id=CHAT_ID,
                text=f"🚨 PEPE düştü: {price:.8f} USDT (Eşik: {THRESHOLD:.8f})"
            )
            print("✅ Uyarı gönderildi.")
        except Exception as e:
            print("❗️ Telegram gönderim hatası:", e)
    else:
        print("ℹ️ Eşik aşılmadı veya CHAT_ID geçersiz.")

if __name__ == "__main__":
    send_signals()
