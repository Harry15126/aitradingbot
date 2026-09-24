import csv
import os
from telegram_notifier import send_telegram_alert

OPEN_TRADES_FILE = "open_trades.csv"


def initialize_open_trades():
    if not os.path.isfile(OPEN_TRADES_FILE):
        with open(OPEN_TRADES_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Pair",
                "Direction",
                "Entry Price",
                "Stop Loss",
                "Take Profit",
                "Risk Amount"
            ])


def get_open_trades():
    initialize_open_trades()

    with open(OPEN_TRADES_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)


def has_open_trade(pair):
    for trade in get_open_trades():
        if trade["Pair"] == pair:
            return True

    return False


def add_open_trade(pair, direction, entry_price, stop_loss, take_profit, risk_amount):
    initialize_open_trades()

    with open(OPEN_TRADES_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            pair,
            direction,
            entry_price,
            stop_loss,
            take_profit,
            risk_amount
        ])

    message = (
        "NEW PAPER TRADE OPENED\n\n"
        f"Pair: {pair}\n"
        f"Direction: {direction}\n"
        f"Entry: {entry_price}\n"
        f"Stop Loss: {stop_loss}\n"
        f"Take Profit: {take_profit}\n"
        f"Risk Amount: ${risk_amount}"
    )

    send_telegram_alert(message)


def remove_open_trade(pair):
    trades = get_open_trades()

    remaining_trades = [
        trade for trade in trades
        if trade["Pair"] != pair
    ]

    with open(OPEN_TRADES_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Pair",
            "Direction",
            "Entry Price",
            "Stop Loss",
            "Take Profit",
            "Risk Amount"
        ])

        for trade in remaining_trades:
            writer.writerow([
                trade["Pair"],
                trade["Direction"],
                trade["Entry Price"],
                trade["Stop Loss"],
                trade["Take Profit"],
                trade["Risk Amount"]
            ])


def show_open_trades():
    trades = get_open_trades()

    print("\n===== OPEN TRADES =====")

    if len(trades) == 0:
        print("No open trades.")
        return

    for trade in trades:
        print("\nPair:", trade["Pair"])
        print("Direction:", trade["Direction"])
        print("Entry:", trade["Entry Price"])
        print("Stop Loss:", trade["Stop Loss"])
        print("Take Profit:", trade["Take Profit"])
        print("Risk Amount:", trade["Risk Amount"])