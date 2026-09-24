import yfinance as yf


FOREX_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "USD/CAD": "USDCAD=X",
    "EUR/JPY": "EURJPY=X",
    "USD/JPY": "USDJPY=X"
}


def get_timeframe_data(ticker, interval, period=None):
    if period is None:
        period = "30d" if interval == "1h" else "5d"

    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    return data


def get_trend_from_data(data):
    if data.empty:
        return "No Data"

    if len(data) < 200:
        return "No Data"

    close = data["Close"]

    latest_price = float(close.iloc[-1].iloc[0])
    ema200 = float(close.ewm(span=200, adjust=False).mean().iloc[-1].iloc[0])

    if latest_price > ema200:
        return "Bullish"

    if latest_price < ema200:
        return "Bearish"

    return "Neutral"


def analyze_multiple_timeframes():
    results = {}

    for pair, ticker in FOREX_PAIRS.items():

        data_15m = get_timeframe_data(ticker, "15m")
        data_1h = get_timeframe_data(ticker, "1h")

        trend_15m = get_trend_from_data(data_15m)
        trend_1h = get_trend_from_data(data_1h)

        if trend_15m == trend_1h:
            confirmation = "Confirmed"
        else:
            confirmation = "Mixed"

        results[pair] = {
            "15m_trend": trend_15m,
            "1h_trend": trend_1h,
            "confirmation": confirmation
        }

    return results


def analyze_pair_timeframe(pair, interval="1h"):
    ticker = FOREX_PAIRS.get(pair)

    if ticker is None:
        return {
            "available": False,
            "pair": pair,
            "interval": interval,
            "trend": "Unknown",
            "message": "Unsupported pair."
        }

    data = get_timeframe_data(ticker, interval)

    if data is None or data.empty:
        return {
            "available": False,
            "pair": pair,
            "interval": interval,
            "trend": "No Data",
            "message": "Higher-timeframe data unavailable."
        }

    return {
        "available": True,
        "pair": pair,
        "interval": interval,
        "trend": get_trend_from_data(data),
        "message": f"{interval} trend calculated."
    }


def trend_supports_trade(trade_bias, higher_timeframe):
    trend = higher_timeframe.get("trend", "Unknown")

    if trade_bias == "BUY ONLY" and trend == "Bullish":
        return True

    if trade_bias == "SELL ONLY" and trend == "Bearish":
        return True

    return False
