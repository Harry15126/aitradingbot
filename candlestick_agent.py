def analyze_candlesticks(data):
    """
    Advanced Candlestick Analysis
    Detects standard patterns and Fair Value Gaps (FVG) based on 3-candle sequences.
    """
    if data is None or data.empty or len(data) < 3:
        return {
            "pattern": "No Data",
            "signal": "Neutral",
            "fvg": {
                "detected": False,
                "type": "None",
                "zone": (0, 0),
                "size": 0,
                "strength": "None"
            }
        }

    # Helpers for clean scalar conversion
    def get_val(val):
        return float(val.iloc[0]) if hasattr(val, "iloc") else float(val)

    # Get data for the last 3 candles
    c1 = data.iloc[-3]  # First candle in sequence
    c2 = data.iloc[-2]  # The impulsive candle (potential gap creator)
    c3 = data.iloc[-1]  # Third candle in sequence

    # Extract values for FVG
    c1_high = get_val(c1["High"])
    c1_low = get_val(c1["Low"])
    c3_high = get_val(c3["High"])
    c3_low = get_val(c3["Low"])

    # Extract values for Pattern Analysis (Last candle only)
    last_open = get_val(c3["Open"])
    last_close = get_val(c3["Close"])
    last_high = get_val(c3["High"])
    last_low = get_val(c3["Low"])

    prev_open = get_val(c2["Open"])
    prev_close = get_val(c2["Close"])

    # --- 1. Fair Value Gap (FVG) Detection ---
    fvg_detected = False
    fvg_type = "None"
    fvg_zone = (0, 0)
    fvg_size = 0
    fvg_strength = "None"

    # Bullish FVG: Gap between C1 High and C3 Low
    if c1_high < c3_low:
        fvg_detected = True
        fvg_type = "Bullish"
        fvg_zone = (c1_high, c3_low)
        fvg_size = c3_low - c1_high
        # Strength based on the impulsive candle (C2) size
        c2_body = abs(get_val(c2["Close"]) - get_val(c2["Open"]))
        fvg_strength = "Strong" if c2_body > (get_val(c2["High"]) - get_val(c2["Low"])) * 0.6 else "Moderate"

    # Bearish FVG: Gap between C1 Low and C3 High
    elif c1_low > c3_high:
        fvg_detected = True
        fvg_type = "Bearish"
        fvg_zone = (c3_high, c1_low)
        fvg_size = c1_low - c3_high
        # Strength based on the impulsive candle (C2) size
        c2_body = abs(get_val(c2["Close"]) - get_val(c2["Open"]))
        fvg_strength = "Strong" if c2_body > (get_val(c2["High"]) - get_val(c2["Low"])) * 0.6 else "Moderate"

    # --- 2. Standard Pattern Analysis (Existing Logic) ---
    body = abs(last_close - last_open)
    candle_range = last_high - last_low

    if candle_range == 0:
        return {
            "pattern": "Invalid Candle",
            "signal": "Neutral",
            "fvg": {"detected": False, "type": "None", "zone": (0, 0), "size": 0, "strength": "None"}
        }

    upper_wick = last_high - max(last_open, last_close)
    lower_wick = min(last_open, last_close) - last_low

    pattern = "No Clear Pattern"
    signal = "Neutral"

    # Bullish engulfing
    if prev_close < prev_open and last_close > last_open and last_close > prev_open and last_open < prev_close:
        pattern = "Bullish Engulfing"
        signal = "Bullish"
    # Bearish engulfing
    elif prev_close > prev_open and last_close < last_open and last_open > prev_close and last_close < prev_open:
        pattern = "Bearish Engulfing"
        signal = "Bearish"
    # Bullish rejection candle
    elif lower_wick > body * 2 and upper_wick < body:
        pattern = "Bullish Rejection Candle"
        signal = "Bullish"
    # Bearish rejection candle
    elif upper_wick > body * 2 and lower_wick < body:
        pattern = "Bearish Rejection Candle"
        signal = "Bearish"
    # Strong bullish candle
    elif last_close > last_open and body > candle_range * 0.6:
        pattern = "Strong Bullish Candle"
        signal = "Bullish"
    # Strong bearish candle
    elif last_close < last_open and body > candle_range * 0.6:
        pattern = "Strong Bearish Candle"
        signal = "Bearish"

    return {
        "pattern": pattern,
        "signal": signal,
        "fvg": {
            "detected": fvg_detected,
            "type": fvg_type,
            "zone": fvg_zone,
            "size": fvg_size,
            "strength": fvg_strength
        }
    }
