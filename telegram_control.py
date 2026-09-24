import json
import os
import time
import requests
from telegram_config import BOT_TOKEN, CHAT_ID_FILE

CONTROL_FILE = "control_state.json"

DEFAULT_CONTROL = {
    "BOT_ACTIVE": True,
    "ALLOW_NEW_TRADES": True,
    "PAPER_TRADING_ONLY": True,
    "MAX_OPEN_TRADES": 2
}


def save_chat_id(chat_id):
    with open(CHAT_ID_FILE, "w") as file:
        file.write(str(chat_id))


def create_control_file_if_missing():
    if not os.path.isfile(CONTROL_FILE):
        with open(CONTROL_FILE, "w") as file:
            json.dump(DEFAULT_CONTROL, file, indent=4)


def load_control():
    create_control_file_if_missing()

    with open(CONTROL_FILE, "r") as file:
        return json.load(file)


def save_control(control):
    with open(CONTROL_FILE, "w") as file:
        json.dump(control, file, indent=4)


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=10
    )


def handle_command(chat_id, text):
    save_chat_id(chat_id)

    control = load_control()

    if text == "/start":
        send_message(
            chat_id,
            "Telegram control connected.\n"
            "You will now receive trading bot alerts."
        )

    elif text == "/status":
        message = (
            "BOT STATUS\n\n"
            f"BOT_ACTIVE: {control['BOT_ACTIVE']}\n"
            f"ALLOW_NEW_TRADES: {control['ALLOW_NEW_TRADES']}\n"
            f"PAPER_TRADING_ONLY: {control['PAPER_TRADING_ONLY']}\n"
            f"MAX_OPEN_TRADES: {control['MAX_OPEN_TRADES']}"
        )
        send_message(chat_id, message)

    elif text == "/pause":
        control["ALLOW_NEW_TRADES"] = False
        save_control(control)
        send_message(chat_id, "New trades paused.")

    elif text == "/resume":
        control["ALLOW_NEW_TRADES"] = True
        save_control(control)
        send_message(chat_id, "New trades resumed.")

    elif text == "/stop":
        control["BOT_ACTIVE"] = False
        save_control(control)
        send_message(chat_id, "Bot stopped.")

    elif text == "/startbot":
        control["BOT_ACTIVE"] = True
        save_control(control)
        send_message(chat_id, "Bot activated.")

    else:
        send_message(
            chat_id,
            "Commands:\n/status\n/pause\n/resume\n/stop\n/startbot"
        )


def run_telegram_control():
    print("\n===== TELEGRAM CONTROL STARTED =====")
    print("Send /start to your Telegram bot.")
    print("Keep this terminal open.")

    last_update_id = None

    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

        params = {
            "timeout": 30
        }

        if last_update_id is not None:
            params["offset"] = last_update_id + 1

        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        data = response.json()

        for update in data.get("result", []):
            last_update_id = update["update_id"]

            message = update.get("message", {})
            chat = message.get("chat", {})
            text = message.get("text", "")
            chat_id = chat.get("id")

            if chat_id and text:
                handle_command(chat_id, text.strip())

        time.sleep(1)


run_telegram_control()