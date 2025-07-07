import os, asyncio
from dotenv import load_dotenv
from advanced_signal_bot import send_signals  

load_dotenv()
asyncio.run(send_signals())
