import pandas as pd


def calculate_atr(data, period=14):

    if data is None or data.empty or len(data) < period + 2:

        return {
            "atr_available": False,
            "atr": 0,
            "volatility_level": "Unknown",
            "message": "Not enough data for ATR."
        }

    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = float(
        true_range.rolling(period).mean().iloc[-1]
    )

    latest_price = float(close.iloc[-1].iloc[0])

    atr_percent = (atr / latest_price) * 100

    if atr_percent < 0.03:

        volatility_level = "Low"

        message = (
            "Volatility is low. Market may be slow."
        )

    elif atr_percent <= 0.12:

        volatility_level = "Normal"

        message = (
            "Volatility is acceptable."
        )

    else:

        volatility_level = "High"

        message = (
            "Volatility is high. Be careful with entries."
        )

    return {
        "atr_available": True,
        "atr": round(atr, 5),
        "atr_percent": round(atr_percent, 4),
        "volatility_level": volatility_level,
        "message": message
    }


def volatility_supports_trade(volatility_result):

    if not volatility_result["atr_available"]:
        return False

    if volatility_result["volatility_level"] == "Normal":
        return True

    return False