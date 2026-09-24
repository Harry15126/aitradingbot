import json
import os

CONTROL_FILE = "control_state.json"

DEFAULT_CONTROL = {
    "BOT_ACTIVE": True,
    "ALLOW_NEW_TRADES": True,
    "PAPER_TRADING_ONLY": True,
    "MAX_OPEN_TRADES": 2
}


def create_control_file_if_missing():
    if not os.path.isfile(CONTROL_FILE):
        with open(CONTROL_FILE, "w") as file:
            json.dump(DEFAULT_CONTROL, file, indent=4)


def load_control():
    create_control_file_if_missing()

    with open(CONTROL_FILE, "r") as file:
        return json.load(file)


control = load_control()

BOT_ACTIVE = control["BOT_ACTIVE"]
ALLOW_NEW_TRADES = control["ALLOW_NEW_TRADES"]
PAPER_TRADING_ONLY = control["PAPER_TRADING_ONLY"]
MAX_OPEN_TRADES = control["MAX_OPEN_TRADES"]