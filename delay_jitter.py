#!/usr/bin/env python3
"""
delay_jitter.py
Year-Round Organic Cadence & History-Aware Anti-Pattern Engine
Dynamically disperses GitHub activity between 2 and 7 commits per day:
- Daily Dynamic Quota: Strictly between 2 and 7 commits/day (maximizing deep green squares)
- Fluid year-round scheduling: Morning, Early Afternoon, Late Afternoon, Evening, Night, Midnight
- Day-of-week sensitivity: Weekends favor daytime hackathons; Weekdays favor evening/night sessions
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
    Computes today's dynamic quota (strictly 2 to 7 commits) and selects
    which time bands and micro-bursts will be active for this date.
    Uses SHA-256 seeding so all runs on the same date agree on the blueprint.
    """
    today_str = today_ist.strftime("%Y-%m-%d")
    is_weekend = today_ist.weekday() >= 5
    
    seed = int(hashlib.sha256(f"status-v2-target-{today_str}".encode()).hexdigest(), 16)
    rng = random.Random(seed)
    
    # Target distribution strictly between 2 and 7:
    # 2 (15%), 3 (25%), 4 (25%), 5 (15%), 6 (10%), 7 (10%)
    roll = rng.randint(1, 100)
    if roll <= 15:
        target = 2
    elif roll <= 40:
        target = 3
    elif roll <= 65:
        target = 4
    elif roll <= 80:
        target = 5
    elif roll <= 92:
        target = 6
    else:
        target = 7

    # Determine windows and micro-burst allocations
    if target > 6:
        windows_needed = 6
        burst_count = target - 6  # 1 burst needed for 7
    else:
        # For targets 3 to 6, 30% chance to consolidate 1 window into a micro-burst
        if target >= 3 and rng.random() < 0.30:
            windows_needed = target - 1
            burst_count = 1
        else:
            windows_needed = target
            burst_count = 0

    # Weights by time band
    # [Morning, Early Afternoon, Late Afternoon, Evening, Night, Midnight]
    if is_weekend:
        weights = [22, 25, 23, 18, 20, 15]
    else:
        weights = [10, 15, 22, 32, 28, 18]

    chosen_indices = []
    candidates = list(range(len(TIME_BANDS)))
    for _ in range(windows_needed):
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
    
    # Select which window gets the micro-burst (if any)
    burst_window_idx = chosen_indices[rng.randint(0, len(chosen_indices) - 1)] if burst_count > 0 else -1

    return target, chosen_indices, burst_window_idx

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
            if abs(prev_minute - target_minute_of_day) < 15:
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
    target_count, active_band_indices, burst_window_idx = plan_day_schedule(now_ist)
    commits_today = count_commits_today(today_str, history)

    active_band_names = [TIME_BANDS[i]["name"] for i in active_band_indices]
    current_band_idx, current_band = detect_current_band(hour_utc)

    print(f"📅 Date (IST): {today_str} ({now_ist.strftime('%A')})")
    print(f"🕒 Current Clock: {now_ist.strftime('%I:%M:%S %p IST')} ({now_utc.strftime('%H:%M:%S UTC')})")
    print(f"🎯 Today's Dynamic Quota: {target_count} commits (Range: 2–7)")
    print(f"🗺️ Active Windows Today: {active_band_names}")
    print(f"📊 Commits completed so far today: {commits_today}")

    # 2. Check if today's quota is already satisfied
    if commits_today >= target_count:
        print(f"✅ Quota satisfied: Already made {commits_today} commit(s) today (Target: {target_count}).")
        print("💤 Skipping this window to preserve natural organic cadence.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 3. Check if current time band is scheduled for today
    if current_band_idx != -1 and current_band_idx not in active_band_indices:
        print(f"💤 Current window '{current_band['name']}' is NOT scheduled for today (Scheduled: {active_band_names}).")
        print("💤 Skipping gracefully to allow activity in today's selected windows.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 4. Calculate Human Jitter Delay (3m to 58m)
    delay_sec = random.randint(180, 3480)
    target_time_ist = now_ist + timedelta(seconds=delay_sec)
    target_minute = target_time_ist.hour * 60 + target_time_ist.minute

    # 5. Anti-Collision Protection
    if check_history_collision(target_minute, history):
        perturb = random.choice([-720, -480, 600, 960, 1200])
        delay_sec = max(120, delay_sec + perturb)
        target_time_ist = now_ist + timedelta(seconds=delay_sec)
        print("🔀 History collision detected: perturbed delay to break repeating time slots.")

    band_name = current_band["name"] if current_band else "Fluid Dynamic"
    print(f"🎯 Active Window: {band_name} | Target Commit Time: {target_time_ist.strftime('%I:%M:%S %p IST')}")
    print(f"⏳ Sleeping for {delay_sec} seconds ({delay_sec // 60}m {delay_sec % 60}s) on GitHub cloud runner...")

    # 6. Micro-Burst Trigger
    # Trigger if this window was chosen for burst OR if remaining quota exceeds remaining windows
    remaining_needed = target_count - commits_today
    if current_band_idx == burst_window_idx or remaining_needed > len(active_band_indices):
        burst_offset = random.randint(240, 660) # 4 to 11 minutes follow-up
        with open(BURST_FLAG_FILE, "w") as f:
            f.write(str(burst_offset))
        print(f"⚡ Natural developer micro-burst scheduled: follow-up commit {burst_offset // 60}m later.")

    time.sleep(delay_sec)
    print("✅ Jitter sleep completed. Handing over to pulse generator.")

if __name__ == "__main__":
    main()
