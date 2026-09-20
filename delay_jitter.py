#!/usr/bin/env python3
"""
delay_jitter.py
Advanced History-Aware Anti-Pattern & Human Behavior Engine
Ensures GitHub contribution commits NEVER follow a predictable schedule or pattern.
- Dynamically varies daily commit volume (1, 2, or 3 commits/day)
- Evaluates recent commit history to prevent time-cluster collisions
- Simulates natural developer micro-bursts (occasional quick follow-up commits)
- Runs 100% in Microsoft/GitHub's cloud runner (zero laptop footprint)
"""

import json
import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta

STATUS_FILE = "pulse.json"
BURST_FLAG_FILE = ".micro_burst"

def get_ist_now():
    now_utc = datetime.now(timezone.utc)
    ist = timezone(timedelta(hours=5, minutes=30))
    return now_utc.astimezone(ist), now_utc

def load_history():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"pulses": [], "daily_stats": {}}

def get_today_target(today_str, history):
    # Seed based on date to maintain consistency for the day, but with entropy
    # Target distribution: 1 commit (30%), 2 commits (55%), 3 commits (15%)
    day_seed = int(today_str.replace("-", ""))
    r = random.Random(day_seed)
    roll = r.randint(1, 100)
    if roll <= 30:
        return 1
    elif roll <= 85:
        return 2
    else:
        return 3

def count_commits_today(today_str, history):
    count = 0
    for p in history.get("pulses", []):
        ts = p.get("timestamp_ist", "")
        if ts.startswith(today_str):
            count += 1
    return count

def check_history_time_collision(target_minute_of_day, history):
    """
    Checks if yesterday or previous days had a commit within 15 minutes of this time.
    If so, returns True to perturb the time.
    """
    recent_pulses = history.get("pulses", [])[:10]
    for p in recent_pulses:
        ts = p.get("timestamp_ist", "")
        # Parse HH:MM from format 'YYYY-MM-DD HH:MM:SS ...'
        try:
            time_part = ts.split(" ")[1]
            hh, mm = map(int, time_part.split(":")[:2])
            prev_minute = hh * 60 + mm
            if abs(prev_minute - target_minute_of_day) < 15:
                return True
        except Exception:
            pass
    return False

def main():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    
    # Clean up any lingering burst flags from previous runs
    if os.path.exists(BURST_FLAG_FILE):
        os.remove(BURST_FLAG_FILE)

    # 1. Manual Dispatch Bypass
    if event_name == "workflow_dispatch":
        print("⚡ Manual workflow_dispatch detected: executing immediately without delay.")
        return

    now_ist, now_utc = get_ist_now()
    today_str = now_ist.strftime("%Y-%m-%d")
    hour_utc = now_utc.hour
    hour_ist = now_ist.hour
    
    history = load_history()
    target_for_today = get_today_target(today_str, history)
    commits_today = count_commits_today(today_str, history)

    print(f"📅 Date (IST): {today_str} | Current Time: {now_ist.strftime('%I:%M:%S %p IST')} ({now_utc.strftime('%H:%M:%S UTC')})")
    print(f"📊 Dynamic Daily Target: {target_for_today} commits | Commits recorded today: {commits_today}")

    # 2. Check if today's quota is already satisfied
    if commits_today >= target_for_today:
        print(f"✅ Quota satisfied: Already made {commits_today} commit(s) today (Target: {target_for_today}).")
        print("💤 Skipping this execution window to preserve organic human cadence and avoid bot patterns.")
        # Exit with a special code or message so workflow can skip commit step
        with open(".skip_run", "w") as f:
            f.write("skip")
        return

    # 3. Dynamic Human Jitter Calculation
    # Determine the window and pick a delay
    # Window 1: Evening Session Start (13:30 - 15:00 UTC / 19:00 - 20:30 IST)
    # Window 2: Mid Evening (15:45 - 17:00 UTC / 21:15 - 22:30 IST)
    # Window 3: Late Night (17:15 - 19:30 UTC / 22:45 - 01:00 IST)
    
    if hour_utc in (13, 14):
        # 19:00 to 20:30 IST
        delay_sec = random.randint(180, 4200) # 3m to 70m
    elif hour_utc in (15, 16):
        # 21:15 to 22:45 IST
        delay_sec = random.randint(180, 4500) # 3m to 75m
    elif hour_utc in (17, 18, 19):
        # 22:45 to 01:00 IST
        delay_sec = random.randint(300, 7200) # 5m to 120m
    else:
        # Fallback window
        delay_sec = random.randint(120, 1800)

    # 4. Anti-Pattern History Collision Check
    target_time_ist = now_ist + timedelta(seconds=delay_sec)
    target_minute = target_time_ist.hour * 60 + target_time_ist.minute
    
    if check_history_time_collision(target_minute, history):
        # Add extra non-repeating perturbation (-18m to +25m)
        perturb = random.choice([-1080, -720, 900, 1380, 1620])
        delay_sec = max(60, delay_sec + perturb)
        target_time_ist = now_ist + timedelta(seconds=delay_sec)
        print("🔀 History collision detected: perturbed delay to break recurring patterns.")

    print(f"🎯 Target commit time: {target_time_ist.strftime('%I:%M:%S %p IST')}")
    print(f"⏳ Sleeping for {delay_sec} seconds ({delay_sec // 60}m {delay_sec % 60}s) on GitHub cloud runner...")
    
    # 5. Check if this commit qualifies for a natural developer "micro-burst"
    # If today's target is 3 or random 20% roll on 2-commit days:
    if target_for_today == 3 and commits_today == 0:
        burst_offset = random.randint(240, 660) # 4 to 11 minutes follow-up
        with open(BURST_FLAG_FILE, "w") as f:
            f.write(str(burst_offset))
        print(f"⚡ Natural micro-burst enabled: secondary commit will trigger {burst_offset // 60}m after primary commit.")

    time.sleep(delay_sec)
    print("✅ Jitter sleep completed. Handing over to pulse generator.")

if __name__ == "__main__":
    main()
