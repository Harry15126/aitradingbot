from open_trade_manager import get_open_trades
from telegram_notifier import send_telegram_alert
import csv

OPEN_TRADES_FILE = "open_trades.csv"


def get_latest_ema(data, period=9):
    close = data["Close"]

    ema = close.ewm(
        span=period,
        adjust=False
    ).mean()

    value = ema.iloc[-1]

    if hasattr(value, "iloc"):
        return float(value.iloc[0])

    return float(value)


def update_trailing_stops(market_data):
    open_trades = get_open_trades()

    if len(open_trades) == 0:
        print("\nNo open trades for trailing stop update.")
        return

    updated_trades = []

    print("\n===== PDF STRATEGY TRAILING MANAGER =====")

    for trade in open_trades:
        pair = trade["Pair"]

        if pair not in market_data or market_data[pair] is None:
            updated_trades.append(trade)
            continue

        data = market_data[pair]
        current_price = float(data["Close"].iloc[-1].iloc[0])
        ema9 = get_latest_ema(data, 9)

        direction = trade["Direction"]
        entry_price = float(trade["Entry Price"])
        stop_loss = float(trade["Stop Loss"])
        take_profit = float(trade["Take Profit"])

        halfway_to_target = (
            entry_price + ((take_profit - entry_price) * 0.5)
            if direction == "BUY"
            else entry_price - ((entry_price - take_profit) * 0.5)
        )

        old_stop_loss = stop_loss

        print("\nPair:", pair)
        print("Direction:", direction)
        print("Current Price:", current_price)
        print("Entry:", entry_price)
        print("Current Stop Loss:", stop_loss)
        print("Take Profit:", take_profit)
        print("50% Target Level:", halfway_to_target)
        print("9 EMA:", ema9)

        if direction == "BUY":
            if current_price >= halfway_to_target and stop_loss < entry_price:
                trade["Stop Loss"] = round(entry_price, 5)
                print("SL moved to breakeven.")

            elif current_price >= halfway_to_target and ema9 > stop_loss:
                new_stop = max(entry_price, ema9)
                trade["Stop Loss"] = round(new_stop, 5)
                print("SL trailed using 9 EMA:", trade["Stop Loss"])

        elif direction == "SELL":
            if current_price <= halfway_to_target and stop_loss > entry_price:
                trade["Stop Loss"] = round(entry_price, 5)
                print("SL moved to breakeven.")

            elif current_price <= halfway_to_target and ema9 < stop_loss:
                new_stop = min(entry_price, ema9)
                trade["Stop Loss"] = round(new_stop, 5)
                print("SL trailed using 9 EMA:", trade["Stop Loss"])

        new_stop_loss = float(trade["Stop Loss"])

        if new_stop_loss != old_stop_loss:
            send_telegram_alert(
                "STOP LOSS UPDATED\n\n"
                f"Pair: {pair}\n"
                f"Direction: {direction}\n"
                f"Old SL: {old_stop_loss}\n"
                f"New SL: {new_stop_loss}\n"
                f"Current Price: {current_price}"
            )

        updated_trades.append(trade)

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

        for trade in updated_trades:
            writer.writerow([
                trade["Pair"],
                trade["Direction"],
                trade["Entry Price"],
                trade["Stop Loss"],
                trade["Take Profit"],
                trade["Risk Amount"]
            ])