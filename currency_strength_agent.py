import yfinance as yf
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

CURRENCIES = ["EUR", "USD", "CAD", "JPY", "AUD", "GBP", "NZD", "CHF"]

REFERENCE_PAIRS = {
    "EURUSD=X": ("EUR", "USD"),
    "USDCAD=X": ("USD", "CAD"),
    "USDJPY=X": ("USD", "JPY"),
    "EURJPY=X": ("EUR", "JPY"),
    "GBPUSD=X": ("GBP", "USD"),
    "AUDUSD=X": ("AUD", "USD"),
    "NZDUSD=X": ("NZD", "USD"),
    "USDCHF=X": ("USD", "CHF"),
    "EURGBP=X": ("EUR", "GBP"),
    "EURCHF=X": ("EUR", "CHF"),
    "GBPJPY=X": ("GBP", "JPY"),
    "AUDJPY=X": ("AUD", "JPY"),
    "CADJPY=X": ("CAD", "JPY"),
    "NZDJPY=X": ("NZD", "JPY"),
    "EURAUD=X": ("EUR", "AUD"),
    "EURCAD=X": ("EUR", "CAD"),
    "GBPAUD=X": ("GBP", "AUD"),
    "AUDCAD=X": ("AUD", "CAD"),
    "AUDNZD=X": ("AUD", "NZD"),
    "GBPCAD=X": ("GBP", "CAD"),
    "CADCHF=X": ("CAD", "CHF"),
    "NZDCHF=X": ("NZD", "CHF"),
    "GBPNZD=X": ("GBP", "NZD"),
}

MIN_STRENGTH_DIFFERENCE = 3
CACHE_TTL_SECONDS = 300


class CurrencyStrengthCache:
    def __init__(self, ttl: int = CACHE_TTL_SECONDS):
        self._cache: Optional[dict] = None
        self._timestamp: float = 0
        self._ttl = ttl

    def get(self) -> Optional[dict]:
        if self._cache is None:
            return None
        if time.time() - self._timestamp > self._ttl:
            return None
        return self._cache

    def set(self, data: dict):
        self._cache = data
        self._timestamp = time.time()

    def clear(self):
        self._cache = None
        self._timestamp = 0


_strength_cache = CurrencyStrengthCache()


def _download_with_retry(ticker: str, max_retries: int = 2, pause: float = 0.5) -> Optional[dict]:
    for attempt in range(max_retries):
        try:
            data = yf.download(
                ticker,
                period="1d",
                interval="15m",
                auto_adjust=True,
                progress=False
            )

            if data.empty or data is None:
                logger.warning(f"No data returned for {ticker}")
                continue

            open_price = float(data["Open"].iloc[0].iloc[0])
            close_price = float(data["Close"].iloc[-1].iloc[0])

            if open_price == 0:
                logger.warning(f"Invalid open price (0) for {ticker}")
                continue

            change_percent = ((close_price - open_price) / open_price) * 100

            return {
                "open": open_price,
                "close": close_price,
                "change_percent": change_percent
            }

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
            if attempt < max_retries - 1:
                time.sleep(pause)

    return None


def calculate_currency_strength(force_refresh: bool = False, use_cache: bool = True) -> dict:
    if use_cache and not force_refresh:
        cached = _strength_cache.get()
        if cached is not None:
            return cached

    scores = {currency: 0 for currency in CURRENCIES}
    magnitude_scores = {currency: 0.0 for currency in CURRENCIES}
    successful_pairs = 0
    failed_pairs = []

    tickers = list(REFERENCE_PAIRS.keys())

    for ticker in tickers:
        result = _download_with_retry(ticker)

        if result is None:
            failed_pairs.append(ticker)
            continue

        base, quote = REFERENCE_PAIRS[ticker]
        change_percent = result["change_percent"]

        if change_percent > 0:
            scores[base] += 1
            scores[quote] -= 1
            magnitude_scores[base] += abs(change_percent)
            magnitude_scores[quote] -= abs(change_percent)
        elif change_percent < 0:
            scores[base] -= 1
            scores[quote] += 1
            magnitude_scores[base] -= abs(change_percent)
            magnitude_scores[quote] += abs(change_percent)

        successful_pairs += 1

    if successful_pairs == 0:
        logger.error("All currency pair downloads failed")
        return {}

    max_score = len(REFERENCE_PAIRS)
    min_score = -len(REFERENCE_PAIRS)

    normalized_scores = {}
    for currency in CURRENCIES:
        score = scores[currency]
        mag = magnitude_scores[currency]

        normalized_scores[currency] = {
            "raw_score": score,
            "magnitude_score": round(mag, 4),
            "strength": max(0, min(8, score + 4)),
            "weighted_strength": max(0, min(8, (score + mag * 0.1) + 4))
        }

    result = {
        "scores": normalized_scores,
        "successful_pairs": successful_pairs,
        "failed_pairs": failed_pairs,
        "timestamp": time.time()
    }

    if use_cache:
        _strength_cache.set(result)

    return result


def get_pair_strength_signal(pair: str, use_weighted: bool = True) -> dict:
    data = calculate_currency_strength()

    if not data:
        return {
            "available": False,
            "signal": "Neutral",
            "difference": 0,
            "message": "Currency strength data unavailable."
        }

    base, quote = pair.split("/")

    if base not in CURRENCIES or quote not in CURRENCIES:
        return {
            "available": False,
            "signal": "Neutral",
            "difference": 0,
            "message": f"Unsupported currency pair: {pair}"
        }

    scores = data["scores"]
    base_data = scores.get(base, {})
    quote_data = scores.get(quote, {})

    if use_weighted:
        base_strength = base_data.get("weighted_strength", 0)
        quote_strength = quote_data.get("weighted_strength", 0)
    else:
        base_strength = base_data.get("strength", 0)
        quote_strength = quote_data.get("strength", 0)

    difference = base_strength - quote_strength

    if difference >= MIN_STRENGTH_DIFFERENCE:
        signal = "BUY"
        message = (
            f"{base} is stronger than {quote}. "
            f"Strength difference: {difference:.1f}"
        )
    elif difference <= -MIN_STRENGTH_DIFFERENCE:
        signal = "SELL"
        message = (
            f"{quote} is stronger than {base}. "
            f"Strength difference: {abs(difference):.1f}"
        )
    else:
        signal = "Neutral"
        message = (
            f"Strength difference is only {abs(difference):.1f}. "
            "No strong currency-strength edge."
        )

    return {
        "available": True,
        "base": base,
        "quote": quote,
        "base_strength": base_strength,
        "quote_strength": quote_strength,
        "base_raw_score": base_data.get("raw_score", 0),
        "quote_raw_score": quote_data.get("raw_score", 0),
        "base_magnitude": base_data.get("magnitude_score", 0),
        "quote_magnitude": quote_data.get("magnitude_score", 0),
        "difference": difference,
        "absolute_difference": abs(difference),
        "signal": signal,
        "message": message,
        "successful_pairs": data.get("successful_pairs", 0),
        "failed_pairs": data.get("failed_pairs", [])
    }


def currency_strength_supports_trade(pair: str, trade_bias: str, use_weighted: bool = True) -> dict:
    strength = get_pair_strength_signal(pair, use_weighted)

    if not strength["available"]:
        return {
            "supported": False,
            "strength": strength,
            "message": "Cannot confirm trade due to missing strength data."
        }

    if trade_bias == "BUY ONLY" and strength["signal"] == "BUY":
        return {
            "supported": True,
            "strength": strength,
            "message": "Currency strength supports BUY setup."
        }

    if trade_bias == "SELL ONLY" and strength["signal"] == "SELL":
        return {
            "supported": True,
            "strength": strength,
            "message": "Currency strength supports SELL setup."
        }

    return {
        "supported": False,
        "strength": strength,
        "message": "Currency strength does not support this setup."
    }


def refresh_strength_cache():
    calculate_currency_strength(force_refresh=True)


def get_strength_cache_status() -> dict:
    data = _strength_cache.get()
    if data is None:
        return {"cached": False}

    age = time.time() - data.get("timestamp", 0)
    return {
        "cached": True,
        "age_seconds": round(age, 1),
        "successful_pairs": data.get("successful_pairs", 0),
        "failed_pairs": data.get("failed_pairs", [])
    }