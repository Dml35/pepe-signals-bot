#!/usr/bin/env python3
# check_alerts.py

import os
import requests
from telegram import Bot
from dotenv import load_dotenv

# 0) .env dosyasını yükle
load_dotenv()

# 1) Ortam değişkenlerini oku ve temizle
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID_RAW = os.getenv("TELEGRAM_CHAT_ID", "").strip()
PEPE_ALERT_LEVEL = os.getenv("PEPE_ALERT_LEVEL", "0").strip()

# 2) CHAT_ID’i güvenli şekilde tamsayıya dönüştür
if CHAT_ID_RAW.isdigit():
    CHAT_ID = int(CHAT_ID_RAW)
else:
    # Geçersizse gönderim yapmayacak
    CHAT_ID = None

# 3) Eşik değerini ondalıklı sayıya dönüştür
try:
    THRESHOLD = float(PEPE_ALERT_LEVEL)
except ValueError:
    THRESHOLD = 0.0

# 4) Bot’u başlat
bot = Bot(token=TOKEN)

def main():
    # 5) Fiyatı Binance API’dan çek
    try:
        resp = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": "PEPEUSDT"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"❗️ API isteği hatası: {e}")
        return

    # 6) JSON’da price anahtarı var mı kontrol et
    price_str = data.get("price")
    if price_str is None:
        print(f"❗️ 'price' bulunamadı, dönen veri: {data}")
        return

    # 7) Ondalıklı sayıya çevir
    try:
        price = float(price_str)
    except ValueError:
        print(f"❗️ 'price' dönüştürülemedi: {price_str}")
        return

    print(f"📊 PEPE fiyatı: {price:.8f} USDT (Eşik={THRESHOLD:.8f})")

    # 8) Eşik altındaysa ve CHAT_ID geçerliyse Telegram’a gönder
    if CHAT_ID and price <= THRESHOLD:
        try:
            bot.send_message(
                chat_id=CHAT_ID,
                text=f"🚨 PEPE düştü: {price:.8f} USDT (Eşik: {THRESHOLD:.8f})"
            )
            print("✅ Uyarı gönderildi.")
        except Exception as e:
            print(f"❗️ Telegram gönderim hatası: {e}")
    else:
        print("ℹ️ Fiyat eşiğin üzerinde veya CHAT_ID geçersiz.")

if __name__ == "__main__":
    main()
