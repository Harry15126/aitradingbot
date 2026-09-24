from oanda_config import (
    OANDA_API_KEY,
    OANDA_ACCOUNT_ID,
    OANDA_ENVIRONMENT
)

print("\n===== ENV TEST =====")

print("Environment:",
      OANDA_ENVIRONMENT)

print("Account ID:",
      OANDA_ACCOUNT_ID)

print(
    "API Key Loaded:",
    OANDA_API_KEY is not None and len(OANDA_API_KEY) > 10
)

print(
    "API Key Length:",
    len(OANDA_API_KEY) if OANDA_API_KEY else 0
)

print(
    "API Key First 5:",
    OANDA_API_KEY[:5] if OANDA_API_KEY else "NONE"
)

print(
    "API Key Last 5:",
    OANDA_API_KEY[-5:] if OANDA_API_KEY else "NONE"
)