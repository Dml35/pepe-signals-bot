import os, requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()
bot     = Bot(token=os.getenv("8019185982:AAFdCNB1hsaK2C3Q3Em6a8UVB6ZZaoKuoH8"))
chat_id = int(os.getenv("845299770"))
threshold = float(os.getenv("PEPE_ALERT_LEVEL", "0.00000720"))

price = float(requests.get(
    "https://api.binance.com/api/v3/ticker/price",
    params={"symbol":"PEPEUSDT"}
).json()["price"])

if price <= threshold:
    bot.send_message(chat_id, f"🚨 PEPE düştü: {price:.8f} USDT")
