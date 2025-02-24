import requests
import time
import os
import telegram

# Configurations
NOTE_URL = os.getenv("NOTE_URL")  # Your Leaflet.pub note URL
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your Telegram bot token
CHAT_ID = os.getenv("CHAT_ID")  # Your Telegram chat ID

last_modified = None

def check_note():
    global last_modified
    try:
        response = requests.head(NOTE_URL)
        if response.status_code == 200:
            new_modified = response.headers.get("Last-Modified")
            if new_modified and new_modified != last_modified:
                last_modified = new_modified
                send_notification("Your shared note has been edited! ✍️")
    except Exception as e:
        print("Error:", e)

def send_notification(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# Run the bot continuously every 10 seconds
while True:
    check_note()
    time.sleep(10)
