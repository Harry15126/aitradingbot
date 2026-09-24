from open_trade_manager import get_open_trades, remove_open_trade
from paper_trader import get_account_balance, update_account_balance, log_paper_trade
from telegram_notifier import send_telegram_alert


def check_trade_exits(market_data, session_name):
    open_trades = get_open_trades()

    if len(open_trades) == 0:
        print("\nNo open trades to check.")
        return

    print("\n===== TRADE EXIT MANAGER =====")

    for trade in open_trades:
        pair = trade["Pair"]

        if pair not in market_data or market_data[pair] is None:
            continue

        data = market_data[pair]
        current_price = float(data["Close"].iloc[-1].iloc[0])

        direction = trade["Direction"]
        stop_loss = float(trade["Stop Loss"])
        take_profit = float(trade["Take Profit"])
        risk_amount = float(trade["Risk Amount"])

        print("\nChecking:", pair)
        print("Current Price:", current_price)

        trade_closed = False
        profit_loss = 0
        result = ""

        if direction == "BUY":
            if current_price <= stop_loss:
                trade_closed = True
                profit_loss = -risk_amount
                result = "STOP LOSS HIT"

            elif current_price >= take_profit:
                trade_closed = True
                profit_loss = risk_amount * 2
                result = "TAKE PROFIT HIT"

        elif direction == "SELL":
            if current_price >= stop_loss:
                trade_closed = True
                profit_loss = -risk_amount
                result = "STOP LOSS HIT"

            elif current_price <= take_profit:
                trade_closed = True
                profit_loss = risk_amount * 2
                result = "TAKE PROFIT HIT"

        if trade_closed:
            balance = get_account_balance()
            new_balance = balance + profit_loss

            update_account_balance(new_balance)
            remove_open_trade(pair)

            trade_result = {
                "trade_taken": True,
                "profit_loss": round(profit_loss, 2),
                "new_balance": round(new_balance, 2)
            }

            log_paper_trade(
                pair,
                session_name,
                True,
                100,
                trade_result
            )

            print(result)
            print("Trade closed.")
            print("Profit/Loss: $", round(profit_loss, 2))
            print("New Balance: $", round(new_balance, 2))

            send_telegram_alert(
                f"{result}\n\n"
                f"Pair: {pair}\n"
                f"Direction: {direction}\n"
                f"Exit Price: {current_price}\n"
                f"Profit/Loss: ${round(profit_loss, 2)}\n"
                f"New Balance: ${round(new_balance, 2)}"
            )

        else:
            print("Trade still open.")