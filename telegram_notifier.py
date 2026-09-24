import os
import requests
from telegram_config import BOT_TOKEN, CHAT_ID_FILE


def get_chat_id():
    if not os.path.isfile(CHAT_ID_FILE):
        return None

    with open(CHAT_ID_FILE, "r") as file:
        return file.read().strip()


def send_telegram_alert(message):
    chat_id = get_chat_id()

    if not chat_id:
        print("Telegram chat ID not found. Send /start to your bot first.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message
            },
            timeout=10
        )

    except Exception as error:
        print("Telegram alert failed:", error)