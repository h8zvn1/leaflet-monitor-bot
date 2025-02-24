import os
import time
import requests
import logging
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread, Event
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBPAGE_URL = os.getenv("WEBPAGE_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 20))  # Default: 20 sec
PROJECT_NAME = os.getenv("PROJECT_NAME", "unknown-project")

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
stop_event = Event()

# Function to send a Telegram message
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",  # Fix for markdown formatting
        "disable_web_page_preview": True  # No link preview
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logging.info("✅ Telegram message sent successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error sending Telegram message: {e} - Response: {response.text}")

# Function to fetch and extract text from the textbox
def fetch_textbox_content(session):
    try:
        response = session.get(WEBPAGE_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text inside the textbox div
        textbox = soup.find("div", class_="blocks w-full flex flex-col outline-none h-fit min-h-full")
        if textbox:
            text = textbox.get_text("\n", strip=True)  # Preserve line breaks
            lines = text.split("\n")  # Split into lines
            
            if len(lines) > 1:
                text_without_first_line = "\n".join(lines[1:])  # Remove the first line
            else:
                text_without_first_line = ""  # If only one line, return empty
            
            return text_without_first_line[:4000]  # Prevent Telegram message length error
        else:
            logging.warning("⚠️ Textbox not found on the webpage.")
            return None
    except requests.exceptions.RequestException as e:
        logging.warning(f"⚠️ Request error: {e}")
        return None


# Background monitoring function
def monitor_website():
    session = requests.Session()
    last_text = fetch_textbox_content(session)

    while not stop_event.is_set():
        time.sleep(CHECK_INTERVAL)
        current_text = fetch_textbox_content(session)

        if current_text is None:
            logging.warning("⚠️ Failed to fetch webpage. Retrying next cycle...")
            continue

        if last_text is not None and current_text != last_text:
            message = (
                "📝 *Textbox Updated!*  \n\n"
                "📌 *New Content:*  \n"
                f"```\n{current_text}\n```  \n\n"
                f"🔗 [View Page]({WEBPAGE_URL})"
            )
            send_telegram_message(message)
            last_text = current_text  # Update stored content

# Flask route for uptime monitoring
@app.route("/")
def home():
    return f"🔄 {PROJECT_NAME} is running!"

# Graceful shutdown
def shutdown():
    stop_event.set()
    logging.info("🛑 Stopping monitoring thread...")

# Start the bot
if __name__ == "__main__":
    monitoring_thread = Thread(target=monitor_website, daemon=True)
    monitoring_thread.start()
    try:
        app.run(host="0.0.0.0", port=3000, debug=False)
    except KeyboardInterrupt:
        shutdown()
