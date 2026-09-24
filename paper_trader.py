import csv
import os
from datetime import datetime, timezone

PAPER_ACCOUNT_FILE = "paper_account.csv"
PAPER_JOURNAL_FILE = "paper_journal.csv"
STRATEGY_SETUPS_FILE = "strategy_setups.csv"


def initialize_account():
    if not os.path.isfile(PAPER_ACCOUNT_FILE):
        with open(PAPER_ACCOUNT_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["balance"])
            writer.writerow([200])


def get_account_balance():
    initialize_account()

    with open(PAPER_ACCOUNT_FILE, mode="r") as file:
        reader = csv.reader(file)
        rows = list(reader)
        return float(rows[1][0])


def update_account_balance(new_balance):
    with open(PAPER_ACCOUNT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["balance"])
        writer.writerow([round(new_balance, 2)])


def log_paper_trade(pair, session, trade_allowed, confidence_score, trade_result):
    file_exists = os.path.isfile(PAPER_JOURNAL_FILE)

    with open(PAPER_JOURNAL_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "UTC Time",
                "Session",
                "Pair",
                "Trade Allowed",
                "Confidence Score",
                "Trade Taken",
                "Profit/Loss",
                "New Balance"
            ])

        writer.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            session,
            pair,
            trade_allowed,
            confidence_score,
            trade_result["trade_taken"],
            trade_result["profit_loss"],
            trade_result["new_balance"]
        ])


def log_strategy_setup(setup_data):
    file_exists = os.path.isfile(STRATEGY_SETUPS_FILE)

    fieldnames = [
        "UTC Time",
        "Session",
        "Session Quality",
        "Pair",
        "Decision",
        "Entry Type",
        "Bias",
        "Price",
        "EMA 200",
        "EMA 9",
        "EMA Distance Pips",
        "1H Trend",
        "1H Trend Supports Trade",
        "ATR",
        "ATR Percent",
        "Volatility Level",
        "Volatility Supports Trade",
        "Quality Grade",
        "Quality Score",
        "SMC Signal",
        "SMC Reason",
        "FVG Detected",
        "FVG Type",
        "FVG Strength",
        "Currency Strength Signal",
        "Currency Strength Difference",
        "Currency Strength Supports Trade",
        "AI Approved",
        "AI Confidence",
        "AI Reason"
    ]

    row = {
        "UTC Time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "Session": setup_data.get("session", ""),
        "Session Quality": setup_data.get("session_quality", ""),
        "Pair": setup_data.get("pair", ""),
        "Decision": setup_data.get("decision", ""),
        "Entry Type": setup_data.get("entry_type", ""),
        "Bias": setup_data.get("bias", ""),
        "Price": setup_data.get("price", ""),
        "EMA 200": setup_data.get("ema200", ""),
        "EMA 9": setup_data.get("ema9", ""),
        "EMA Distance Pips": setup_data.get("ema_distance_pips", ""),
        "1H Trend": setup_data.get("higher_timeframe_trend", ""),
        "1H Trend Supports Trade": setup_data.get("higher_timeframe_supported", ""),
        "ATR": setup_data.get("atr", ""),
        "ATR Percent": setup_data.get("atr_percent", ""),
        "Volatility Level": setup_data.get("volatility_level", ""),
        "Volatility Supports Trade": setup_data.get("volatility_supported", ""),
        "Quality Grade": setup_data.get("quality_grade", ""),
        "Quality Score": setup_data.get("quality_score", ""),
        "SMC Signal": setup_data.get("smc_signal", ""),
        "SMC Reason": setup_data.get("smc_reason", ""),
        "FVG Detected": setup_data.get("fvg_detected", ""),
        "FVG Type": setup_data.get("fvg_type", ""),
        "FVG Strength": setup_data.get("fvg_strength", ""),
        "Currency Strength Signal": setup_data.get("currency_strength_signal", ""),
        "Currency Strength Difference": setup_data.get("currency_strength_difference", ""),
        "Currency Strength Supports Trade": setup_data.get("currency_strength_supported", ""),
        "AI Approved": setup_data.get("ai_approved", ""),
        "AI Confidence": setup_data.get("ai_confidence", ""),
        "AI Reason": setup_data.get("ai_reason", "")
    }

    with open(STRATEGY_SETUPS_FILE, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
