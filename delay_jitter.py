#!/usr/bin/env python3
"""
delay_jitter.py
Simulates authentic human developer cadence by introducing random time jitter.
Ensures GitHub contribution commits land at completely natural, randomized times
within designated human coding windows (e.g. 19:00-20:00 IST and 22:00-01:00 IST).
Runs 100% in GitHub's cloud runner (zero laptop footprint).
"""

import os
import random
import time
from datetime import datetime, timezone, timedelta

def main():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    
    # If triggered manually via GitHub UI, run immediately without delay
    if event_name == "workflow_dispatch":
        print("⚡ Manual workflow_dispatch detected: executing immediately without delay.")
        return

    # Check current UTC hour
    now_utc = datetime.now(timezone.utc)
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = now_utc.astimezone(ist)
    hour_utc = now_utc.hour

    print(f"🕒 Current UTC Time: {now_utc.strftime('%H:%M:%S UTC')} | Current IST Time: {now_ist.strftime('%H:%M:%S IST')}")

    # Window 1: Evening Session Start (13:30 UTC = 19:00 IST)
    # Target: Random minute between 19:00 and 20:00 IST (2 to 55 minutes delay)
    if hour_utc in (13, 14):
        delay_sec = random.randint(120, 3300)
        target_ist = now_ist + timedelta(seconds=delay_sec)
        print(f"🎯 Window 1 (Session Start 19:00 - 20:00 IST) selected.")
        print(f"🎲 Random human jitter delay: {delay_sec // 60}m {delay_sec % 60}s")
        print(f"📅 Target execution time: {target_ist.strftime('%H:%M:%S IST')}")

    # Window 2: Late Night Wrap-up (16:30 UTC = 22:00 IST)
    # Target: Random minute between 22:00 and 01:00 IST (5 to 160 minutes delay)
    elif hour_utc in (16, 17, 18, 19):
        delay_sec = random.randint(300, 9600)
        target_ist = now_ist + timedelta(seconds=delay_sec)
        print(f"🎯 Window 2 (Session Wrap-up 22:00 - 01:00 IST) selected.")
        print(f"🎲 Random human jitter delay: {delay_sec // 60}m {delay_sec % 60}s")
        print(f"📅 Target execution time: {target_ist.strftime('%H:%M:%S IST')}")

    else:
        # Default fallback jitter (1 to 20 minutes)
        delay_sec = random.randint(60, 1200)
        print(f"🎲 Default random jitter delay: {delay_sec // 60}m {delay_sec % 60}s")

    print(f"⏳ Sleeping for {delay_sec} seconds on GitHub cloud runner...")
    time.sleep(delay_sec)
    print("✅ Delay complete. Proceeding with status pulse update.")

if __name__ == "__main__":
    main()
