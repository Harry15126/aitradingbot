from datetime import datetime, timezone

MAJOR_PAIRS = ["EUR/USD", "USD/CAD", "EUR/JPY", "USD/JPY"]


def get_current_session():
    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour

    if 0 <= hour < 7:
        session = "Asian Session"
    elif 7 <= hour < 12:
        session = "London Session"
    elif 12 <= hour < 16:
        session = "London/New York Overlap"
    elif 16 <= hour < 21:
        session = "New York Session"
    else:
        session = "Late New York / Low Liquidity"

    if session in ["London Session", "London/New York Overlap"]:
        session_quality = "High"
    elif session in ["New York Session", "Asian Session"]:
        session_quality = "Medium"
    else:
        session_quality = "Low"

    return {
        "utc_time": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "session": session,
        "session_quality": session_quality
    }


def london_session_agent():
    session_info = get_current_session()

    print("\n===== LONDON SESSION AGENT =====")
    print("Current UTC Time:", session_info["utc_time"])
    print("Current Session:", session_info["session"])
    print("Pairs checked:", MAJOR_PAIRS)

    return session_info


def new_york_session_agent():
    session_info = get_current_session()

    print("\n===== NEW YORK SESSION AGENT =====")
    print("Current UTC Time:", session_info["utc_time"])
    print("Current Session:", session_info["session"])
    print("Pairs checked:", MAJOR_PAIRS)

    return session_info
