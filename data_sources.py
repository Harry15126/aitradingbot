import yfinance as yf

FOREX_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "USD/CAD": "USDCAD=X",
    "EUR/JPY": "EURJPY=X",
    "USD/JPY": "USDJPY=X"
}


def get_forex_data():
    market_data = {}

    for pair_name, ticker in FOREX_PAIRS.items():
        data = yf.download(
            ticker,
            period="5d",
            interval="15m",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            market_data[pair_name] = None
        else:
            market_data[pair_name] = data

    return market_data