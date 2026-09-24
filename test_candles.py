from data_sources import get_forex_data
from candlestick_agent import analyze_candlesticks

market_data = get_forex_data()

for pair, data in market_data.items():
    candle = analyze_candlesticks(data)

    print("\n---", pair, "---")
    print("Pattern:", candle["pattern"])
    print("Signal:", candle["signal"])