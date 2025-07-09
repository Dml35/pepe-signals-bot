#!/usr/bin/env python3
import os
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN       = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID_RAW = os.getenv("TELEGRAM_CHAT_ID", "").strip()

if CHAT_ID_RAW.isdigit():
    CHAT_ID = int(CHAT_ID_RAW)
else:
    CHAT_ID = None

bot = Bot(token=TOKEN)

def main():
    # örnek alert: 1₺ altındaki BTC alarımı
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
    if not price_str:
        print("❗️ 'price' yok, veri:", data)
        return

    try:
        price = float(price_str)
    except:
        print("❗️ 'price' parse hatası:", price_str)
        return

    print(f"📊 {symbol} = {price:.8f} USDT")
    # örnek eşik:
    alert_level = 10000.0
    if CHAT_ID and price <= alert_level:
        try:
            bot.send_message(
                chat_id=CHAT_ID,
                text=f"⚠️ {symbol} {price:.8f} USDT’ye düştü! (Eşik: {alert_level})"
            )
            print("✅ Alert gönderildi.")
        except Exception as e:
            print("❗️ Telegram gönderim hatası:", e)
    else:
        print("ℹ️ Fiyat eşiğin üzerinde veya CHAT_ID geçersiz.")

if __name__ == "__main__":
    main()
