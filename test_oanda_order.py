from oanda_broker import place_market_order

place_market_order(
    pair="EUR/USD",
    direction="BUY",
    units=1,

    stop_loss=1.15000,
    take_profit=1.17000
)