import json
import os
from datetime import datetime, timezone

NEWS_FILE = "news_events.json"

NEWS_AVOID_MINUTES_BEFORE = 30
NEWS_AVOID_MINUTES_AFTER = 30


def get_pair_currencies(pair):
    base, quote = pair.split("/")
    return [base, quote]


def load_news_events():
    if not os.path.isfile(NEWS_FILE):
        return {
            "date": None,
            "events": []
        }

    with open(NEWS_FILE, "r") as file:
        return json.load(file)


def check_news_risk(pair):
    news_data = load_news_events()

    today = datetime.now(timezone.utc).date().isoformat()

    if news_data.get("date") != today:
        return {
            "news_risk": False,
            "event": "No updated news file for today",
            "currency": "None",
            "message": "Daily news file not updated today."
        }

    now = datetime.now(timezone.utc)
    pair_currencies = get_pair_currencies(pair)

    for event in news_data.get("events", []):
        if event["impact"] != "High":
            continue

        if event["currency"] not in pair_currencies:
            continue

        # --- Robust Time Parsing ---
        utc_time = event.get("utc_time")
        if not utc_time or utc_time == "Unknown" or not isinstance(utc_time, str):
            continue

        try:
            time_parts = utc_time.split(":")
            if len(time_parts) != 2:
                continue
            hour = int(time_parts[0])
            minute = int(time_parts[1])
        except (ValueError, IndexError):
            # Skip event if time is not in valid HH:MM format
            continue

        event_time = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        minutes_before = (
            event_time - now
        ).total_seconds() / 60

        minutes_after = (
            now - event_time
        ).total_seconds() / 60

        if (
            0 <= minutes_before <= NEWS_AVOID_MINUTES_BEFORE
            or
            0 <= minutes_after <= NEWS_AVOID_MINUTES_AFTER
        ):
            return {
                "news_risk": True,
                "event": event["event"],
                "currency": event["currency"],
                "message": "Avoid trading near high-impact news."
            }

    return {
        "news_risk": False,
        "event": "No nearby high-impact event",
        "currency": "None",
        "message": "No major news risk detected."
    }
