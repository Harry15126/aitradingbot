ACCOUNT_BALANCE = 200

RISK_PER_TRADE_NORMAL = 0.01
RISK_PER_TRADE_MAX = 0.02

DAILY_MAX_LOSS = 0.03

RISK_REWARD_RATIO = 2
TRAILING_START_R = 1.5

MIN_STOP_LOSS_PIPS = 10
MAX_STOP_LOSS_PIPS = 50


def calculate_pips(entry_price, stop_loss_price):

    pip_difference = abs(entry_price - stop_loss_price)

    if entry_price > 20:
        pips = pip_difference * 100
    else:
        pips = pip_difference * 10000

    return round(pips, 1)


def evaluate_stop_loss(stop_loss_pips):

    if stop_loss_pips < MIN_STOP_LOSS_PIPS:
        return "BAD - Stop loss too tight"

    elif stop_loss_pips > MAX_STOP_LOSS_PIPS:
        return "BAD - Stop loss too wide"

    else:
        return "GOOD - Stop loss acceptable"


def calculate_lot_size(risk_amount, stop_loss_pips):

    if stop_loss_pips == 0:
        return 0

    lot_size = risk_amount / stop_loss_pips

    return round(lot_size, 2)


def calculate_risk_plan(account_balance,
                        entry_price,
                        stop_loss_price):

    risk_amount = account_balance * RISK_PER_TRADE_NORMAL

    stop_loss_pips = calculate_pips(
        entry_price,
        stop_loss_price
    )

    stop_loss_quality = evaluate_stop_loss(stop_loss_pips)

    lot_size = calculate_lot_size(
        risk_amount,
        stop_loss_pips
    )

    risk_per_unit = abs(entry_price - stop_loss_price)

    if entry_price > stop_loss_price:

        direction = "BUY"

        take_profit = (
            entry_price +
            (risk_per_unit * RISK_REWARD_RATIO)
        )

    else:

        direction = "SELL"

        take_profit = (
            entry_price -
            (risk_per_unit * RISK_REWARD_RATIO)
        )

    trade_allowed = stop_loss_quality.startswith("GOOD")

    return {

        "direction": direction,

        "account_balance": account_balance,

        "risk_amount": round(risk_amount, 2),

        "entry_price": round(entry_price, 5),

        "stop_loss": round(stop_loss_price, 5),

        "take_profit": round(take_profit, 5),

        "risk_reward": "2:1",

        "stop_loss_pips": stop_loss_pips,

        "stop_loss_quality": stop_loss_quality,

        "recommended_lot_size": lot_size,

        "trade_allowed": trade_allowed,

        "trailing_stop_rule":
            "Move stop loss after 1.5R profit",

        "overnight_rule":
            "Hold overnight only if trade remains profitable"
    }