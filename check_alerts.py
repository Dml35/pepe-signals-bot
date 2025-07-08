import os
import requests
from dotenv import load_dotenv
from telegram import Bot

# .env dosyasını yükle (yerelde test için)
load_dotenv()

# 1) ENV VAR’LARI İSİM ÜZERİNDEN AL
TOKEN     = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_RAW  = os.getenv("TELEGRAM_CHAT_ID", "0")
threshold = float(os.getenv("PEPE_ALERT_LEVEL", "0.00000720"))

# 2) CHAT_ID’I GÜVENLİ PARSE ET
chat_id = int(CHAT_RAW) if CHAT_RAW.isdigit() else 0

# 3) Bot’u başlat
bot = Bot(token=TOKEN)

# 4) Fiyatı çek ve eşiği kontrol et
price = float(requests.get(
    "https://api.binance.com/api/v3/ticker/price",
    params={"symbol": "PEPEUSDT"},
    timeout=10
).json()["price"])

if price <= threshold:
    bot.send_message(chat_id=chat_id, text=f"🚨 PEPE düştü: {price:.8f} USDT")
