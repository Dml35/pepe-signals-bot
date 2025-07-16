# PEPE Signals Bot

This repository contains a small Telegram bot that periodically checks the PEPE/USDT price on Binance and optionally notifies a Telegram chat when the price drops below a configured threshold.

## Requirements
- Python 3
- A Telegram bot token and chat ID

Dependencies are listed in [`requirements.txt`](requirements.txt). Install them with:

```bash
pip install -r requirements.txt
```

## Environment Variables
Before running the bot you need to set the following variables:

- `TELEGRAM_BOT_TOKEN` – token for your Telegram bot
- `TELEGRAM_CHAT_ID` – numeric chat ID where alerts will be sent
- `PEPE_ALERT_LEVEL` – price threshold that triggers a PEPE alert

These can be exported in your shell or placed in a `.env` file.

## Running Locally
After installing the dependencies and defining the environment variables, run:

```bash
python send_signals.py
```

This will fetch the PEPE price and send a Telegram message if the price is below the provided `PEPE_ALERT_LEVEL`.

The repository also contains `check_alerts.py` which performs a similar check for Bitcoin prices.

## GitHub Actions
The workflow defined in [`.github/workflows/bot.yml`](.github/workflows/bot.yml) runs on GitHub Actions every 10 minutes and on manual dispatch. It installs the dependencies and executes both scripts with the environment variables taken from repository secrets.
