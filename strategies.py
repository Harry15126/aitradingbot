def get_float(data, column, index=-1):
    value = data[column].iloc[index]

    if hasattr(value, "iloc"):
        return float(value.iloc[0])

    return float(value)


def calculate_rsi(data, period=14):
    close = data["Close"]

    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    value = rsi.iloc[-1]

    if hasattr(value, "iloc"):
        return float(value.iloc[0])

    return float(value)


def calculate_ema(data, period):
    close = data["Close"]
    ema = close.ewm(span=period, adjust=False).mean()
    value = ema.iloc[-1]

    if hasattr(value, "iloc"):
        return float(value.iloc[0])

    return float(value)


def calculate_pips(price_difference, price):
    if price > 20:
        return abs(price_difference) * 100

    return abs(price_difference) * 10000


def find_support_resistance(data):
    latest_price = get_float(data, "Close")

    recent_high = float(data["High"].tail(50).max().iloc[0])
    recent_low = float(data["Low"].tail(50).min().iloc[0])

    return {
        "support": recent_low,
        "resistance": recent_high,
        "distance_to_support": latest_price - recent_low,
        "distance_to_resistance": recent_high - latest_price
    }


def ema_200_intraday_strategy(data):
    if data is None or data.empty or len(data) < 220:
        return {
            "price": 0,
            "rsi": 50,
            "trend": "Neutral",
            "bias": "WAIT",
            "support": 0,
            "resistance": 0,
            "stop_loss_zone": 0,
            "strategy_name": "200 EMA Intraday Strategy",
            "entry_type": "No Data",
            "ema200": 0,
            "ema9": 0,
            "ema_distance_pips": 0,
            "strategy_reason": "Not enough candle data."
        }

    price = get_float(data, "Close")
    high = get_float(data, "High")
    low = get_float(data, "Low")

    ema200 = calculate_ema(data, 200)
    ema9 = calculate_ema(data, 9)
    rsi = calculate_rsi(data)

    zones = find_support_resistance(data)

    recent_high = float(data["High"].iloc[-21:-1].max().iloc[0])
    recent_low = float(data["Low"].iloc[-21:-1].min().iloc[0])

    distance_from_ema = price - ema200
    ema_distance_pips = calculate_pips(distance_from_ema, price)

    ideal_distance = 10 <= ema_distance_pips <= 50
    too_far_from_ema = ema_distance_pips > 60

    tolerance = abs(price - ema200) * 0.0015

    pullback_long = (
        price > ema200
        and low <= ema200 + tolerance
        and ideal_distance
    )

    pullback_short = (
        price < ema200
        and high >= ema200 - tolerance
        and ideal_distance
    )

    new_high_breakout = (
        price > ema200
        and price > recent_high
        and ideal_distance
    )

    new_low_breakdown = (
        price < ema200
        and price < recent_low
        and ideal_distance
    )

    if price > ema200:
        trend = "Bullish"
    elif price < ema200:
        trend = "Bearish"
    else:
        trend = "Neutral"

    bias = "WAIT"
    entry_type = "No Entry"
    strategy_reason = "No valid 200 EMA setup."

    if too_far_from_ema:
        strategy_reason = "Price is too far from 200 EMA. Avoid bad RR."

    elif pullback_long:
        bias = "BUY ONLY"
        entry_type = "Pullback to 200 EMA"
        strategy_reason = "Bullish pullback entry near 200 EMA."

    elif pullback_short:
        bias = "SELL ONLY"
        entry_type = "Pullback to 200 EMA"
        strategy_reason = "Bearish pullback entry near 200 EMA."

    elif new_high_breakout:
        bias = "BUY ONLY"
        entry_type = "New High Breakout"
        strategy_reason = "Price broke new high above 200 EMA."

    elif new_low_breakdown:
        bias = "SELL ONLY"
        entry_type = "New Low Breakdown"
        strategy_reason = "Price broke new low below 200 EMA."

    if bias == "BUY ONLY":
        stop_loss_zone = min(zones["support"], ema200)
    elif bias == "SELL ONLY":
        stop_loss_zone = max(zones["resistance"], ema200)
    else:
        stop_loss_zone = zones["support"]

    return {
        "price": price,
        "sma20": ema9,
        "sma50": ema200,
        "rsi": rsi,
        "trend": trend,
        "bias": bias,
        "support": zones["support"],
        "resistance": zones["resistance"],
        "distance_to_support": zones["distance_to_support"],
        "distance_to_resistance": zones["distance_to_resistance"],
        "stop_loss_zone": stop_loss_zone,
        "strategy_name": "200 EMA Intraday Strategy",
        "entry_type": entry_type,
        "ema200": ema200,
        "ema9": ema9,
        "ema_distance_pips": round(ema_distance_pips, 1),
        "strategy_reason": strategy_reason
    }


def analyze_pair(data):
    return ema_200_intraday_strategy(data)