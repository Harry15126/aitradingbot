def analyze_market_structure(data):
    """
    Advanced Market Structure Analysis
    Detects Swing points, Liquidity Sweeps, BOS, and CHOCH/MSS.
    """
    if data is None or data.empty or len(data) < 60:
        return {
            "structure": "No Data",
            "bos": False,
            "choch": False,
            "sweep": False,
            "signal": "Neutral",
            "reason": "Not enough data"
        }

    highs = data["High"]
    lows = data["Low"]
    close = data["Close"]

    # Use float conversion for pandas Series scalars
    def get_val(val):
        return float(val.iloc[0]) if hasattr(val, "iloc") else float(val)

    latest_close = get_val(close.iloc[-1])
    latest_high = get_val(highs.iloc[-1])
    latest_low = get_val(lows.iloc[-1])

    # 1. Swing Point Detection (Simplified Window)
    # Recent window (last 20) vs Previous window (-60 to -20)
    recent_high = get_val(highs.tail(20).max())
    recent_low = get_val(lows.tail(20).min())
    previous_high = get_val(highs.iloc[-60:-20].max())
    previous_low = get_val(lows.iloc[-60:-20].min())

    # 2. Liquidity Sweep Detection
    # Buy-side sweep: High penetrates previous high but closes below it
    buy_sweep = latest_high > previous_high and latest_close < previous_high
    # Sell-side sweep: Low penetrates previous low but closes above it
    sell_sweep = latest_low < previous_low and latest_close > previous_low

    sweep = False
    sweep_type = "None"
    if buy_sweep:
        sweep = True
        sweep_type = "Buy-side"
    elif sell_sweep:
        sweep = True
        sweep_type = "Sell-side"

    # 3. BOS (Break of Structure) - Trend Continuation
    bos = False
    bos_type = "None"
    if latest_close > previous_high:
        bos = True
        bos_type = "Bullish BOS"
    elif latest_close < previous_low:
        bos = True
        bos_type = "Bearish BOS"

    # 4. CHOCH / MSS (Change of Character / Market Structure Shift) - Trend Reversal
    choch = False

    # Determine current general structure
    higher_high = recent_high > previous_high
    higher_low = recent_low > previous_low
    lower_high = recent_high < previous_high
    lower_low = recent_low < previous_low

    if higher_high and higher_low:
        structure = "Bullish Structure"
        # Bearish CHOCH: Bullish structure but close breaks recent low
        if latest_close < recent_low:
            choch = True
    elif lower_high and lower_low:
        structure = "Bearish Structure"
        # Bullish CHOCH: Bearish structure but close breaks recent high
        if latest_close > recent_high:
            choch = True
    else:
        structure = "Range / Mixed Structure"

    # 5. Signal Output and Reason logic
    signal = "Neutral"
    reason = "Market structure is ranging or neutral."

    # Priority: CHOCH > Sweep > BOS > General Structure
    if choch:
        if structure == "Bullish Structure": # became bearish
            signal = "Bearish"
            reason = "Bearish CHOCH: Market shifted from bullish to bearish structure."
        else: # became bullish
            signal = "Bullish"
            reason = "Bullish CHOCH: Market shifted from bearish to bullish structure."
    elif sweep:
        if buy_sweep:
            signal = "Bearish"
            reason = f"Buy-side Liquidity Sweep detected at {previous_high}."
        else:
            signal = "Bullish"
            reason = f"Sell-side Liquidity Sweep detected at {previous_low}."
    elif bos:
        if bos_type == "Bullish BOS":
            signal = "Bullish"
            reason = "Bullish Break of Structure: Continuing upward trend."
        else:
            signal = "Bearish"
            reason = "Bearish Break of Structure: Continuing downward trend."
    elif structure == "Bullish Structure":
        signal = "Bullish"
        reason = "Consistent Bullish structure (HH/HL)."
    elif structure == "Bearish Structure":
        signal = "Bearish"
        reason = "Consistent Bearish structure (LH/LL)."

    return {
        "structure": structure,
        "bos": bos,
        "choch": choch,
        "sweep": sweep,
        "signal": signal,
        "reason": reason,
        "recent_high": recent_high,
        "recent_low": recent_low,
        "previous_high": previous_high,
        "previous_low": previous_low,
        "sweep_type": sweep_type,
        "bos_type": bos_type
    }
