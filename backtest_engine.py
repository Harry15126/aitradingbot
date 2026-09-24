from data_sources import get_forex_data
from strategies import analyze_pair
from currency_strength_agent import (
    currency_strength_supports_trade
)

START_BALANCE = 200
RISK_PER_TRADE = 2
RR_RATIO = 2

wins = 0
losses = 0
trades_taken = 0
total_profit = 0

print("\n===== 200 EMA STRATEGY BACKTEST STARTED =====")

market_data = get_forex_data()

balance = START_BALANCE


def get_float(data, column, index):
    value = data[column].iloc[index]

    if hasattr(value, "iloc"):
        return float(value.iloc[0])

    return float(value)


def test_trade_outcome(
    pair,
    data,
    start_index,
    direction,
    entry,
    stop_loss,
    take_profit
):

    future_data = data.iloc[start_index + 1:start_index + 40]

    for _, candle in future_data.iterrows():

        high = float(candle["High"].iloc[0])
        low = float(candle["Low"].iloc[0])

        if direction == "BUY":

            if low <= stop_loss:
                return "LOSS"

            if high >= take_profit:
                return "WIN"

        else:

            if high >= stop_loss:
                return "LOSS"

            if low <= take_profit:
                return "WIN"

    return "NO_RESULT"


for pair, data in market_data.items():

    print(f"\n===== BACKTESTING {pair} =====")

    if data is None or data.empty or len(data) < 300:
        print("Not enough data.")
        continue

    pair_trades = 0
    pair_wins = 0
    pair_losses = 0
    pair_profit = 0

    for index in range(250, len(data) - 40):

        historical_data = data.iloc[:index]

        result = analyze_pair(historical_data)

        if result["bias"] == "WAIT":
            continue

        strength_filter = currency_strength_supports_trade(
            pair,
            result["bias"]
        )

        if not strength_filter["supported"]:
            continue

        entry = result["price"]
        stop_loss = result["stop_loss_zone"]

        if result["bias"] == "BUY ONLY":

            direction = "BUY"

            risk_distance = entry - stop_loss

            if risk_distance <= 0:
                continue

            take_profit = entry + (risk_distance * RR_RATIO)

        else:

            direction = "SELL"

            risk_distance = stop_loss - entry

            if risk_distance <= 0:
                continue

            take_profit = entry - (risk_distance * RR_RATIO)

        outcome = test_trade_outcome(
            pair,
            data,
            index,
            direction,
            entry,
            stop_loss,
            take_profit
        )

        if outcome == "NO_RESULT":
            continue

        trades_taken += 1
        pair_trades += 1

        if outcome == "WIN":

            wins += 1
            pair_wins += 1

            profit = RISK_PER_TRADE * RR_RATIO

            total_profit += profit
            pair_profit += profit

            balance += profit

        else:

            losses += 1
            pair_losses += 1

            total_profit -= RISK_PER_TRADE
            pair_profit -= RISK_PER_TRADE

            balance -= RISK_PER_TRADE

    if pair_trades > 0:
        pair_win_rate = (pair_wins / pair_trades) * 100
    else:
        pair_win_rate = 0

    print("Trades:", pair_trades)
    print("Wins:", pair_wins)
    print("Losses:", pair_losses)
    print("Win Rate:", round(pair_win_rate, 2), "%")
    print("Profit/Loss: $", round(pair_profit, 2))

print("\n===== FINAL BACKTEST REPORT =====")

if trades_taken > 0:
    overall_win_rate = (wins / trades_taken) * 100
else:
    overall_win_rate = 0

print("Total Trades:", trades_taken)
print("Total Wins:", wins)
print("Total Losses:", losses)
print("Overall Win Rate:", round(overall_win_rate, 2), "%")
print("Total Profit/Loss: $", round(total_profit, 2))
print("Starting Balance: $", START_BALANCE)
print("Final Balance: $", round(balance, 2))