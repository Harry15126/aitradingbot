from execution_mode import EXECUTION_MODE
from open_trade_manager import add_open_trade
from oanda_broker import place_market_order

OANDA_DEMO_FIXED_UNITS = 1


def execute_trade(pair, risk_plan):

    direction = risk_plan["direction"]
    entry_price = risk_plan["entry_price"]
    stop_loss = risk_plan["stop_loss"]
    take_profit = risk_plan["take_profit"]
    risk_amount = risk_plan["risk_amount"]

    if EXECUTION_MODE == "paper":

        add_open_trade(
            pair,
            direction,
            entry_price,
            stop_loss,
            take_profit,
            risk_amount
        )

        print("\nExecution Mode: PAPER")
        print("Paper trade opened.")

        return {
            "executed": True,
            "mode": "paper"
        }

    if EXECUTION_MODE == "oanda_demo":

        print("\nExecution Mode: OANDA DEMO")
        print("Sending fixed 1-unit practice order only.")

        place_market_order(
            pair=pair,
            direction=direction,
            units=OANDA_DEMO_FIXED_UNITS,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        return {
            "executed": True,
            "mode": "oanda_demo"
        }

    if EXECUTION_MODE == "live":

        print("\nLIVE EXECUTION IS BLOCKED FOR SAFETY.")
        return {
            "executed": False,
            "mode": "live_blocked"
        }

    print("\nUnknown execution mode. No trade executed.")

    return {
        "executed": False,
        "mode": "unknown"
    }