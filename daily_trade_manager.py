import csv
import os
from datetime import datetime, timezone

PAPER_JOURNAL_FILE = "paper_journal.csv"
MAX_TRADES_PER_DAY = 8


def get_today_trade_count():
    if not os.path.isfile(PAPER_JOURNAL_FILE):
        return 0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    trade_count = 0

    with open(PAPER_JOURNAL_FILE, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            utc_time = row["UTC Time"]
            trade_taken = row["Trade Taken"] == "True"

            if utc_time.startswith(today) and trade_taken:
                trade_count += 1

    return trade_count


def daily_trade_limit_reached():
    today_trades = get_today_trade_count()

    return {
        "today_trades": today_trades,
        "max_trades_per_day": MAX_TRADES_PER_DAY,
        "limit_reached": today_trades >= MAX_TRADES_PER_DAY
    }