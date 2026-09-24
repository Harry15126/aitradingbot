import yfinance as yf


def get_dxy_analysis():
    data = yf.download(
        "DX-Y.NYB",
        period="5d",
        interval="15m",
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        return {
            "dxy_available": False,
            "dxy_trend": "No Data",
            "dxy_bias": "Unknown"
        }

    close = data["Close"]

    latest_price = float(close.iloc[-1].iloc[0])
    sma20 = float(close.rolling(20).mean().iloc[-1].iloc[0])
    sma50 = float(close.rolling(50).mean().iloc[-1].iloc[0])

    if sma20 > sma50:
        dxy_trend = "Bullish"
        dxy_bias = "USD Strong"
    elif sma20 < sma50:
        dxy_trend = "Bearish"
        dxy_bias = "USD Weak"
    else:
        dxy_trend = "Neutral"
        dxy_bias = "Mixed"

    return {
        "dxy_available": True,
        "dxy_price": round(latest_price, 3),
        "dxy_sma20": round(sma20, 3),
        "dxy_sma50": round(sma50, 3),
        "dxy_trend": dxy_trend,
        "dxy_bias": dxy_bias
    }


def check_dxy_pair_alignment(pair, trade_bias, dxy_bias):
    if trade_bias == "WAIT":
        return "No trade bias"

    if pair in ["EUR/USD"]:
        if trade_bias == "BUY ONLY" and dxy_bias == "USD Weak":
            return "Aligned"
        elif trade_bias == "SELL ONLY" and dxy_bias == "USD Strong":
            return "Aligned"
        else:
            return "Conflict"

    if pair in ["USD/CAD", "USD/JPY"]:
        if trade_bias == "BUY ONLY" and dxy_bias == "USD Strong":
            return "Aligned"
        elif trade_bias == "SELL ONLY" and dxy_bias == "USD Weak":
            return "Aligned"
        else:
            return "Conflict"

    if pair == "EUR/JPY":
        return "Neutral - DXY indirect"

    return "Unknown"