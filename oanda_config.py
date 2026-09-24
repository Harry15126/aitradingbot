from dotenv import load_dotenv
import os

load_dotenv()

OANDA_ENVIRONMENT = "practice"

OANDA_API_KEY = os.getenv("OANDA_API_KEY", "").strip()
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", "").strip()