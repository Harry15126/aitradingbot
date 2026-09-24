import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from bs4 import BeautifulSoup

NEWS_FILE = "news_events.json"

FOREX_FACTORY_XML_URL = (
    "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
)

FXSTREET_URL = (
    "https://www.fxstreet.com/economic-calendar"
)

OANDA_CALENDAR_URL = (
    "https://www.oanda.com/eu-en/calendar/economic"
)

IMPORTANT_CURRENCIES = [
    "USD",
    "CAD",
    "EUR",
    "JPY",
    "GBP",
    "AUD",
    "NZD",
    "CHF"
]


def safe_request(url):
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0"
                )
            }
        )

        if response.status_code == 200:
            return response

        print("Failed:", url)
        print("Status:", response.status_code)

        return None

    except Exception as error:
        print("Request failed:", url)
        print(error)
        return None


# =====================================================
# FOREX FACTORY XML
# =====================================================

def parse_forex_factory_time(date_text, time_text):
    try:
        combined = f"{date_text} {time_text}"

        event_time = datetime.strptime(
            combined,
            "%m-%d-%Y %I:%M%p"
        )

        return event_time.strftime("%H:%M")

    except Exception:
        return None



def fetch_forex_factory_events():
    response = safe_request(
        FOREX_FACTORY_XML_URL
    )

    if response is None:
        return []

    root = ET.fromstring(response.content)

    events = []

    for event in root.findall("event"):
        title = event.findtext("title", default="")
        country = event.findtext("country", default="")
        date_text = event.findtext("date", default="")
        time_text = event.findtext("time", default="")
        impact = event.findtext("impact", default="")

        if country not in IMPORTANT_CURRENCIES:
            continue

        if impact.lower() != "high":
            continue

        utc_time = parse_forex_factory_time(
            date_text,
            time_text
        )

        if utc_time is None:
            continue

        events.append({
            "currency": country,
            "event": title,
            "impact": "High",
            "utc_time": utc_time,
            "source": "Forex Factory"
        })

    return events


# =====================================================
# FXSTREET
# =====================================================

def fetch_fxstreet_events():
    response = safe_request(FXSTREET_URL)

    if response is None:
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    events = []

    rows = soup.find_all("tr")

    for row in rows:
        text = row.get_text(" ", strip=True)

        if not text:
            continue

        if "High" not in text:
            continue

        found_currency = None

        for currency in IMPORTANT_CURRENCIES:
            if currency in text:
                found_currency = currency
                break

        if not found_currency:
            continue

        events.append({
            "currency": found_currency,
            "event": text[:120],
            "impact": "High",
            "utc_time": "Unknown",
            "source": "FXStreet"
        })

    return events[:20]


# =====================================================
# OANDA CALENDAR
# =====================================================

def fetch_oanda_events():
    response = safe_request(
        OANDA_CALENDAR_URL
    )

    if response is None:
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    text = soup.get_text(" ", strip=True)

    events = []

    keywords = [
        "Interest Rate",
        "CPI",
        "GDP",
        "Employment",
        "FOMC",
        "NFP"
    ]

    for keyword in keywords:
        if keyword in text:
            events.append({
                "currency": "USD",
                "event": keyword,
                "impact": "High",
                "utc_time": "Unknown",
                "source": "OANDA"
            })

    return events


# =====================================================
# MAIN NEWS BUILDER
# =====================================================

def remove_duplicate_events(events):
    seen = set()
    unique_events = []

    for event in events:
        key = (
            event["currency"],
            event["event"]
        )

        if key in seen:
            continue

        seen.add(key)
        unique_events.append(event)

    return unique_events



def create_daily_news_file():
    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    print("\n===== FETCHING NEWS SOURCES =====")

    forex_factory_events = (
        fetch_forex_factory_events()
    )

    fxstreet_events = (
        fetch_fxstreet_events()
    )

    oanda_events = (
        fetch_oanda_events()
    )

    all_events = (
        forex_factory_events
        + fxstreet_events
        + oanda_events
    )

    all_events = remove_duplicate_events(
        all_events
    )

    data = {
        "date": today,
        "events": all_events
    }

    with open(NEWS_FILE, "w") as file:
        json.dump(
            data,
            file,
            indent=4
        )

    print("\n===== DAILY NEWS AGENT =====")

    print(
        "Total High Impact Events:",
        len(all_events)
    )

    for event in all_events:
        print(
            f"[{event['source']}]",
            event["currency"],
            event["event"]
        )

    print("\nNews file updated:", NEWS_FILE)


create_daily_news_file()