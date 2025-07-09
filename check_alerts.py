#!/usr/bin/env python3
import os
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Env’ler
TOKEN_RAW   = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_RAW    = os.getenv("TELEGRAM_CHAT_ID", "").strip()

if not TOKEN_RAW:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN boş!")
TOKEN = TOKEN_RAW

try:
    CHAT_ID = int(CHAT_RAW)
except ValueError:
    CHAT_ID = None

bot = Bot(token=TOKEN)

def main():
    symbol = "BTCUSDT"
    url = "https://api.binance.com/api/v3/ticker/price"
    try:
        r = requests.get(url, params={"symbol": symbol}, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("❗️ API isteği hatası:", e)
        return

    price_str = data.get("price")
    if price_str is None:
        print("❗️ 'price' yok, veri:", data)
        return

    try:
        price = float(price_str)
    except ValueError:
        print("❗️ 'price' parse hatası:", price_str)
        return

    print(f"📊 {symbol} fiyatı: {price:.8f} USDT")
    alert_level = 10000.0
    if CHAT_ID and price <= alert_level:
        text = f"⚠️ {symbol} {price:.8f} USDT’ye düştü! (Eşik: {alert_level})"
        try:
            bot.send_message(chat_id=CHAT_ID, text=text)
            print("✅ Alert gönderildi.")
        except Exception as e:
            print("❗️ Telegram gönderim hatası:", e)
    else:
        print("ℹ️ Fiyat eşiğin üzerinde veya CHAT_ID geçersiz.")

if __name__ == "__main__":
    main()
