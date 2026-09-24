import requests
from oanda_config import (
    OANDA_API_KEY,
    OANDA_ACCOUNT_ID,
    OANDA_ENVIRONMENT
)

if OANDA_ENVIRONMENT == "practice":
    BASE_URL = "https://api-fxpractice.oanda.com"
else:
    BASE_URL = "https://api-fxtrade.oanda.com"

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}

OANDA_INSTRUMENTS = {
    "EUR/USD": "EUR_USD",
    "USD/CAD": "USD_CAD",
    "EUR/JPY": "EUR_JPY",
    "USD/JPY": "USD_JPY"
}


def get_account_info():

    url = f"{BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    if response.status_code != 200:
        print("\nFailed to connect to OANDA.")
        print("Status Code:", response.status_code)
        print(response.text)
        return None

    data = response.json()

    return data["account"]


def get_oanda_price(pair):

    instrument = OANDA_INSTRUMENTS.get(pair)

    if not instrument:
        return None

    url = f"{BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/pricing"

    response = requests.get(
        url,
        headers=HEADERS,
        params={
            "instruments": instrument
        },
        timeout=15
    )

    if response.status_code != 200:
        print("\nFailed to get price for", pair)
        print("Status Code:", response.status_code)
        print(response.text)
        return None

    data = response.json()

    price_data = data["prices"][0]

    bid = float(price_data["bids"][0]["price"])
    ask = float(price_data["asks"][0]["price"])

    mid = (bid + ask) / 2

    return {
        "pair": pair,
        "instrument": instrument,
        "bid": bid,
        "ask": ask,
        "mid": round(mid, 5)
    }


def place_market_order(
    pair,
    direction,
    units,
    stop_loss,
    take_profit
):

    instrument = OANDA_INSTRUMENTS.get(pair)

    if not instrument:
        print("Unsupported pair:", pair)
        return None

    if direction == "SELL":
        units = -abs(units)
    else:
        units = abs(units)

    url = f"{BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"

    order_data = {
        "order": {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(units),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",

            "stopLossOnFill": {
                "price": str(round(stop_loss, 5))
            },

            "takeProfitOnFill": {
                "price": str(round(take_profit, 5))
            }
        }
    }

    response = requests.post(
        url,
        headers=HEADERS,
        json=order_data,
        timeout=15
    )

    print("\n===== OANDA ORDER RESPONSE =====")
    print("Status Code:", response.status_code)
    print(response.text)

    return response.json()


def show_oanda_status():

    account = get_account_info()

    if account is None:
        return

    print("\n===== OANDA CONNECTION SUCCESS =====")

    print("Account ID:",
          account["id"])

    print("Currency:",
          account["currency"])

    print("Balance:",
          account["balance"])

    print("Open Trades:",
          account["openTradeCount"])

    print("Open Positions:",
          account["openPositionCount"])

    print("Margin Available:",
          account["marginAvailable"])

    print("Unrealized P/L:",
          account["unrealizedPL"])

    print("\n===== OANDA LIVE PRICES =====")

    for pair in OANDA_INSTRUMENTS:

        price = get_oanda_price(pair)

        if price:

            print("\nPair:",
                  price["pair"])

            print("Bid:",
                  price["bid"])

            print("Ask:",
                  price["ask"])

            print("Mid:",
                  price["mid"])


if __name__ == "__main__":
    show_oanda_status()