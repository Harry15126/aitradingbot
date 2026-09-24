import csv
import os
from datetime import datetime, timezone

PAPER_JOURNAL_FILE = "paper_journal.csv"
DAILY_MAX_LOSS_AMOUNT = 6.00


def get_today_loss():
    if not os.path.isfile(PAPER_JOURNAL_FILE):
        return 0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_loss = 0

    with open(PAPER_JOURNAL_FILE, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            utc_time = row["UTC Time"]
            profit_loss = float(row["Profit/Loss"])

            if utc_time.startswith(today) and profit_loss < 0:
                total_loss += abs(profit_loss)

    return round(total_loss, 2)


def daily_loss_limit_reached():
    today_loss = get_today_loss()

    return {
        "today_loss": today_loss,
        "daily_max_loss": DAILY_MAX_LOSS_AMOUNT,
        "limit_reached": today_loss >= DAILY_MAX_LOSS_AMOUNT
    }
