from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import sys


def run_trading_system():
    print("\n===== LIVE PAPER SCAN STARTED =====")

    subprocess.run([
        sys.executable,
        "main.py"
    ])

    print("\n===== LIVE PAPER SCAN COMPLETE =====")


def run_daily_news_agent():
    print("\n===== DAILY NEWS UPDATE STARTED =====")

    subprocess.run([
        sys.executable,
        "daily_news_agent.py"
    ])

    print("\n===== DAILY NEWS UPDATE COMPLETE =====")


scheduler = BlockingScheduler()

# Trading scan every 15 minutes
scheduler.add_job(
    run_trading_system,
    "cron",
    minute="*/15"
)

# Daily news update once per day
# 01:00 Vancouver time roughly = 08:00 UTC during daylight saving
scheduler.add_job(
    run_daily_news_agent,
    "cron",
    hour=8,
    minute=0
)

print("\n===== BOT SCHEDULER STARTED =====")
print("Trading scan: every 15 minutes")
print("Daily news update: 08:00 UTC")
print("Keep this terminal open.")

# Run news agent once immediately at startup too
run_daily_news_agent()

scheduler.start()