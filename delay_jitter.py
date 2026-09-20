#!/usr/bin/env python3
"""
delay_jitter.py
Year-Round Organic Cadence & History-Aware Anti-Pattern Engine
Dynamically disperses GitHub activity across the entire 24-hour day throughout the year:
- Fluid year-round scheduling: Morning, Early Afternoon, Late Afternoon, Evening, Night, Midnight
- Day-of-week sensitivity: Weekends skew towards daytime hackathons; Weekdays skew towards evening/night sessions
- Daily dynamic targets: Varies between 1, 2, and 3 commits/day
- History-aware collision avoidance (≥15-25m delta from prior days)
- Developer micro-bursts (occasional follow-up commit 4-11 minutes later)
- 100% cloud-executed on GitHub Actions (zero laptop footprint)
"""

import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta

STATUS_FILE = "pulse.json"
BURST_FLAG_FILE = ".micro_burst"
SKIP_FLAG_FILE = ".skip_run"

# 6 Natural Daily Time Bands (IST)
TIME_BANDS = [
    {"name": "Morning",         "utc_trigger": "04:30", "ist_base": "10:00", "hours_utc": (4, 5)},
    {"name": "Early Afternoon", "utc_trigger": "07:30", "ist_base": "13:00", "hours_utc": (7, 8)},
    {"name": "Late Afternoon",  "utc_trigger": "10:30", "ist_base": "16:00", "hours_utc": (10, 11)},
    {"name": "Evening",         "utc_trigger": "13:30", "ist_base": "19:00", "hours_utc": (13, 14)},
    {"name": "Night",           "utc_trigger": "16:00", "ist_base": "21:30", "hours_utc": (15, 16, 17)},
    {"name": "Midnight",        "utc_trigger": "18:30", "ist_base": "00:00", "hours_utc": (18, 19, 20)}
]

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
    return {"pulses": []}

def count_commits_today(today_str, history):
    count = 0
    for p in history.get("pulses", []):
        ts = p.get("timestamp_ist", "")
        if ts.startswith(today_str):
            count += 1
    return count

def plan_day_schedule(today_ist):
    """
    Computes today's dynamic quota (1, 2, or 3) and selects which time bands
    will be active for this specific calendar date throughout the year.
    Uses SHA-256 seeding so all runs on the same date agree on the day's plan.
    """
    today_str = today_ist.strftime("%Y-%m-%d")
    is_weekend = today_ist.weekday() >= 5
    
    seed = int(hashlib.sha256(f"status-{today_str}".encode()).hexdigest(), 16)
    rng = random.Random(seed)
    
    # Target distribution: 1 commit (30%), 2 commits (55%), 3 commits (15%)
    roll = rng.randint(1, 100)
    if roll <= 30:
        target = 1
    elif roll <= 85:
        target = 2
    else:
        target = 3

    # Weights by time band
    # [Morning, Early Afternoon, Late Afternoon, Evening, Night, Midnight]
    if is_weekend:
        # Weekends: high daytime hackathons
        weights = [20, 25, 25, 20, 20, 15]
    else:
        # Weekdays: high late afternoon/evening/night, but morning/lunch still happen
        weights = [10, 15, 20, 35, 30, 15]

    chosen_indices = []
    candidates = list(range(len(TIME_BANDS)))
    for _ in range(target):
        total_w = sum(weights[i] for i in candidates)
        pick_val = rng.uniform(0, total_w)
        cum = 0
        for idx in candidates:
            cum += weights[idx]
            if cum >= pick_val:
                chosen_indices.append(idx)
                candidates.remove(idx)
                break

    chosen_indices.sort()
    return target, chosen_indices

def detect_current_band(hour_utc):
    for idx, band in enumerate(TIME_BANDS):
        if hour_utc in band["hours_utc"]:
            return idx, band
    return -1, None

def check_history_collision(target_minute_of_day, history):
    recent_pulses = history.get("pulses", [])[:10]
    for p in recent_pulses:
        ts = p.get("timestamp_ist", "")
        try:
            time_part = ts.split(" ")[1]
            hh, mm = map(int, time_part.split(":")[:2])
            prev_minute = hh * 60 + mm
            if abs(prev_minute - target_minute_of_day) < 18:
                return True
        except Exception:
            pass
    return False

def main():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    
    # Cleanup flags from prior runs
    for f in (BURST_FLAG_FILE, SKIP_FLAG_FILE):
        if os.path.exists(f):
            os.remove(f)

    # 1. Manual Dispatch Bypass
    if event_name == "workflow_dispatch":
        print("⚡ Manual workflow_dispatch detected: executing immediately without delay.")
        return

    now_ist, now_utc = get_ist_now()
    today_str = now_ist.strftime("%Y-%m-%d")
    hour_utc = now_utc.hour

    history = load_history()
    target_count, active_band_indices = plan_day_schedule(now_ist)
    commits_today = count_commits_today(today_str, history)

    active_band_names = [TIME_BANDS[i]["name"] for i in active_band_indices]
    current_band_idx, current_band = detect_current_band(hour_utc)

    print(f"📅 Date (IST): {today_str} ({now_ist.strftime('%A')})")
    print(f"🕒 Current Clock: {now_ist.strftime('%I:%M:%S %p IST')} ({now_utc.strftime('%H:%M:%S UTC')})")
    print(f"🎯 Today's Dynamic Target: {target_count} commit(s) | Active Bands Today: {active_band_names}")
    print(f"📊 Commits already completed today: {commits_today}")

    # 2. Check if today's quota is already satisfied
    if commits_today >= target_count:
        print(f"✅ Quota satisfied: Already made {commits_today} commit(s) today (Target: {target_count}).")
        print("💤 Skipping this window to maintain natural cadence.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 3. Check if the current time band was chosen for today
    if current_band_idx != -1 and current_band_idx not in active_band_indices:
        print(f"💤 Current window '{current_band['name']}' is NOT scheduled for today (Scheduled: {active_band_names}).")
        print("💤 Skipping gracefully to let activity occur in today's selected windows.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 4. Calculate Human Jitter Delay
    # Jitter range: 4 minutes to 62 minutes
    delay_sec = random.randint(240, 3720)
    target_time_ist = now_ist + timedelta(seconds=delay_sec)
    target_minute = target_time_ist.hour * 60 + target_time_ist.minute

    # 5. History Collision Avoidance
    if check_history_collision(target_minute, history):
        perturb = random.choice([-900, -600, 720, 1200, 1500])
        delay_sec = max(180, delay_sec + perturb)
        target_time_ist = now_ist + timedelta(seconds=delay_sec)
        print("🔀 History collision detected: perturbed delay to break repeating time-clusters.")

    band_name = current_band["name"] if current_band else "Fluid Dynamic"
    print(f"🎯 Window: {band_name} | Target Commit Time: {target_time_ist.strftime('%I:%M:%S %p IST')}")
    print(f"⏳ Sleeping for {delay_sec} seconds ({delay_sec // 60}m {delay_sec % 60}s) on GitHub cloud runner...")

    # 6. Micro-Burst Simulation (20% chance on multi-commit days)
    if target_count == 3 and commits_today == 0:
        burst_offset = random.randint(240, 660) # 4 to 11 minutes
        with open(BURST_FLAG_FILE, "w") as f:
            f.write(str(burst_offset))
        print(f"⚡ Natural micro-burst enabled: secondary commit will follow {burst_offset // 60}m after.")

    time.sleep(delay_sec)
    print("✅ Jitter sleep completed. Handing over to pulse generator.")

if __name__ == "__main__":
    main()
