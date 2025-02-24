import time
import requests
import os

# Telegram Bot Credentials (For Sending Alerts)
TELEGRAM_BOT_TOKEN = "7510809128:AAHtbrWzrQeV6O3M9kyIyh5E9veEArovMtg"
TELEGRAM_CHAT_ID = "7661236020"

# Your Glitch Bot's URL
GLITCH_URL = "https://YOUR_GLITCH_PROJECT_NAME.glitch.me/"

def send_telegram_alert(message):
    """Send a Telegram alert if the Glitch bot is down."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"⚠️ *Glitch Bot Down!*  \n\n🔗 [Check Glitch]({GLITCH_URL})",
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

while True:
    try:
        response = requests.get(GLITCH_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Glitch bot is online.")
        else:
            print("❌ Glitch bot is DOWN!")
            send_telegram_alert("Glitch bot is not responding!")
    except requests.exceptions.RequestException:
        print("❌ Glitch bot is unreachable!")
        send_telegram_alert("Glitch bot is not reachable!")

    time.sleep(300)  # Check every 5 minutes
