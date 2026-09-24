import csv
import os
from collections import defaultdict

PAPER_JOURNAL_FILE = "paper_journal.csv"
PAPER_ACCOUNT_FILE = "paper_account.csv"


def get_current_balance():
    if not os.path.isfile(PAPER_ACCOUNT_FILE):
        return 200

    with open(PAPER_ACCOUNT_FILE, mode="r") as file:
        rows = list(csv.reader(file))

        if len(rows) < 2:
            return 200

        return float(rows[1][0])


def show_performance_report():
    if not os.path.isfile(PAPER_JOURNAL_FILE):
        print("\nNo paper journal found yet.")
        return

    total_trades = 0
    wins = 0
    losses = 0
    total_profit_loss = 0

    pair_stats = defaultdict(
        lambda: {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "profit_loss": 0
        }
    )

    with open(PAPER_JOURNAL_FILE, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            trade_taken = row["Trade Taken"] == "True"
            profit_loss = float(row["Profit/Loss"])
            pair = row["Pair"]

            if not trade_taken:
                continue

            if profit_loss == 0:
                continue

            total_trades += 1
            total_profit_loss += profit_loss

            pair_stats[pair]["trades"] += 1
            pair_stats[pair]["profit_loss"] += profit_loss

            if profit_loss > 0:
                wins += 1
                pair_stats[pair]["wins"] += 1

            elif profit_loss < 0:
                losses += 1
                pair_stats[pair]["losses"] += 1

    if total_trades > 0:
        win_rate = (wins / total_trades) * 100
    else:
        win_rate = 0

    print("\n===== PAPER TRADING PERFORMANCE REPORT =====")
    print("Current Paper Balance: $", get_current_balance())
    print("Closed Trades:", total_trades)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win Rate:", round(win_rate, 2), "%")
    print("Total Profit/Loss: $", round(total_profit_loss, 2))

    print("\n===== PAIR PERFORMANCE =====")

    if len(pair_stats) == 0:
        print("No closed trades yet.")
        return

    for pair, stats in pair_stats.items():
        trades = stats["trades"]

        if trades > 0:
            pair_win_rate = (stats["wins"] / trades) * 100
        else:
            pair_win_rate = 0

        print("\nPair:", pair)
        print("Trades:", trades)
        print("Wins:", stats["wins"])
        print("Losses:", stats["losses"])
        print("Win Rate:", round(pair_win_rate, 2), "%")
        print("Profit/Loss: $", round(stats["profit_loss"], 2))


show_performance_report()