from data_sources import get_forex_data
from open_trade_manager import get_open_trades


def calculate_pips(pair, price_difference):
    if "JPY" in pair:
        return price_difference * 100

    return price_difference * 10000


def monitor_open_trades():
    trades = get_open_trades()
    market_data = get_forex_data()

    print("\n===== LIVE OPEN TRADE MONITOR =====")

    if len(trades) == 0:
        print("No open trades.")
        return

    for trade in trades:
        pair = trade["Pair"]

        if pair not in market_data or market_data[pair] is None:
            print("\nNo live data for:", pair)
            continue

        data = market_data[pair]
        current_price = float(data["Close"].iloc[-1].iloc[0])

        direction = trade["Direction"]
        entry_price = float(trade["Entry Price"])
        stop_loss = float(trade["Stop Loss"])
        take_profit = float(trade["Take Profit"])

        risk_distance = abs(entry_price - stop_loss)

        if direction == "BUY":
            price_move = current_price - entry_price
            distance_to_tp = take_profit - current_price
            distance_to_sl = current_price - stop_loss

        else:
            price_move = entry_price - current_price
            distance_to_tp = current_price - take_profit
            distance_to_sl = stop_loss - current_price

        unrealized_pips = calculate_pips(pair, price_move)

        if risk_distance == 0:
            unrealized_r = 0
        else:
            unrealized_r = price_move / risk_distance

        print("\nPair:", pair)
        print("Direction:", direction)
        print("Entry:", entry_price)
        print("Current Price:", current_price)
        print("Stop Loss:", stop_loss)
        print("Take Profit:", take_profit)
        print("Unrealized Pips:", round(unrealized_pips, 1))
        print("Unrealized R:", round(unrealized_r, 2))

        if unrealized_r >= 1.5:
            print("Status: Strong profit zone. Trailing stop should be active.")

        elif unrealized_r > 0:
            print("Status: Trade is in profit.")

        elif unrealized_r == 0:
            print("Status: Near entry.")

        else:
            print("Status: Trade is currently negative.")


monitor_open_trades()