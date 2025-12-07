#!/usr/bin/env python3
import os
import requests
from telegram import Bot
from dotenv import load_dotenv
from typing import Optional

load_dotenv()  # Local’da .env’den, CI’da env’den çeker

# —————————————————————————————
# 1) Env’leri oku ve strip ile temizle
TOKEN_RAW      = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID_RAW    = os.getenv("TELEGRAM_CHAT_ID", "").strip()
PEPE_LEVEL_RAW = os.getenv("PEPE_ALERT_LEVEL", "0").strip()

# 2) TOKEN kontrolü
if not TOKEN_RAW:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN boş!")
TOKEN = TOKEN_RAW

# 3) CHAT_ID’i güvenli parse et
try:
    CHAT_ID = int(CHAT_ID_RAW)
except ValueError:
    CHAT_ID = None

# 4) Eşik değerini float’a çevir
try:
    THRESHOLD = float(PEPE_LEVEL_RAW)
except ValueError:
    THRESHOLD = 0.0

bot = Bot(token=TOKEN)

def get_pepe_price() -> Optional[float]:
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": "PEPEUSDT"}
    try:
        r = requests.get(url, params=params, timeout=10)
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
    except ValueError:
        print("❗️ 'price' float’a çevrilemedi:", price_str)
        return None

def send_signals():
    price = get_pepe_price()
    if price is None:
        return

    print(f"📊 PEPE fiyatı: {price:.8f} USDT — Eşik = {THRESHOLD:.8f}")
    if CHAT_ID and price <= THRESHOLD:
        text = f"🚨 PEPE düştü: {price:.8f} USDT (Eşik: {THRESHOLD:.8f})"
        try:
            bot.send_message(chat_id=CHAT_ID, text=text)
            print("✅ Uyarı gönderildi.")
        except Exception as e:
            print("❗️ Telegram gönderim hatası:", e)
    else:
        print("ℹ️ Eşik aşılmadı veya CHAT_ID geçersiz.")

if __name__ == "__main__":
    send_signals()
