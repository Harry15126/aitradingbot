from open_trade_manager import get_open_trades


def show_open_trade_report():
    trades = get_open_trades()

    print("\n===== OPEN TRADE REPORT =====")

    if len(trades) == 0:
        print("No open trades right now.")
        return

    for trade in trades:
        print("\nPair:", trade["Pair"])
        print("Direction:", trade["Direction"])
        print("Entry:", trade["Entry Price"])
        print("Stop Loss:", trade["Stop Loss"])
        print("Take Profit:", trade["Take Profit"])
        print("Risk Amount: $", trade["Risk Amount"])


if __name__ == "__main__":
    show_open_trade_report()