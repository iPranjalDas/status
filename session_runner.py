#!/usr/bin/env python3
"""
session_runner.py
Developer Session Clustering & Fluid Multi-Commit Engine
Simulates authentic human developer sessions:
- Makes 2 to 6 commits in the SAME session with realistic coding intervals (8–23 min gaps)
- Supports split days: e.g. Morning single commit (10:23) + Evening cluster (17:48, 18:09) or vice versa
- Daily volume: Strictly between 2 and 7 commits per day
- Rotates conventional commit scopes and modifies telemetry/README
- 100% cloud-executed on GitHub Actions (zero laptop footprint)
"""

import hashlib
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

import update_status

STATUS_FILE = "pulse.json"
SKIP_FLAG_FILE = ".skip_run"

# 6 Daily Windows (IST Base Times)
TIME_WINDOWS = [
    {"name": "Morning",         "ist_start": "10:00", "hours_utc": (4, 5)},
    {"name": "Early Afternoon", "ist_start": "13:00", "hours_utc": (7, 8)},
    {"name": "Late Afternoon",  "ist_start": "16:00", "hours_utc": (10, 11)},
    {"name": "Evening",         "ist_start": "17:30", "hours_utc": (12, 13, 14)},
    {"name": "Night",           "ist_start": "21:30", "hours_utc": (15, 16, 17)},
    {"name": "Midnight",        "ist_start": "00:00", "hours_utc": (18, 19, 20)}
]

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if res.returncode != 0:
        print(f"Command failed: {cmd}\n{res.stderr}")
        return False, res.stderr
    return True, res.stdout

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

def plan_day_blueprint(today_ist):
    """
    Creates a deterministic blueprint for the day based on date:
    - Daily Target: 2 to 7 commits
    - Sessions: [commits_in_session_1] or [commits_in_session_1, commits_in_session_2]
    - Windows: assigns each session to an active time window
    """
    today_str = today_ist.strftime("%Y-%m-%d")
    is_weekend = today_ist.weekday() >= 5

    seed = int(hashlib.sha256(f"blueprint-v3-{today_str}".encode()).hexdigest(), 16)
    rng = random.Random(seed)

    # 1. Target between 2 and 7 commits
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

    # 2. Determine session clustering:
    # 50% single focused session (all 2-6 commits in one session)
    # 50% split session (e.g. 1 morning + 2-5 evening, or vice versa)
    if target == 2:
        session_sizes = [2] if rng.random() < 0.55 else [1, 1]
    else:
        if rng.random() < 0.45:
            session_sizes = [target]  # Cluster of 3 to 7 commits in one session
        else:
            if rng.random() < 0.65:
                s1 = 1
                s2 = target - 1
            else:
                s1 = rng.randint(2, target - 1)
                s2 = target - s1
            # Randomize order (e.g. 1 then 3, or 3 then 1)
            session_sizes = [s1, s2] if rng.random() < 0.5 else [s2, s1]

    # 3. Assign windows to sessions
    # Early windows (Morning: 0, Early Afternoon: 1, Late Afternoon: 2)
    # Late windows (Evening: 3, Night: 4, Midnight: 5)
    sessions = []
    if len(session_sizes) == 1:
        # Single session: pick best window depending on weekday/weekend
        if is_weekend:
            w_idx = rng.choice([0, 1, 2, 3])  # Weekend favors daytime
        else:
            w_idx = rng.choice([2, 3, 4])     # Weekday favors late afternoon / evening / night
        sessions.append({"window_idx": w_idx, "commits": session_sizes[0]})
    else:
        # Two sessions: Session 1 in earlier band, Session 2 in later band
        early_candidates = [0, 1, 2] if is_weekend else [0, 1, 2]
        late_candidates = [3, 4, 5]
        w1_idx = rng.choice(early_candidates)
        w2_idx = rng.choice(late_candidates)
        sessions.append({"window_idx": w1_idx, "commits": session_sizes[0]})
        sessions.append({"window_idx": w2_idx, "commits": session_sizes[1]})

    return target, sessions

def detect_current_window(hour_utc):
    for idx, w in enumerate(TIME_WINDOWS):
        if hour_utc in w["hours_utc"]:
            return idx, w
    return -1, None

def execute_session(num_commits, is_manual=False):
    """
    Executes a developer coding session with realistic in-session pauses
    between commits (8 to 23 minutes between commits).
    """
    print(f"\n🚀 Starting Developer Coding Session: {num_commits} commit(s) planned.")
    
    run_cmd('git config --global user.name "Pranjal Das"')
    run_cmd('git config --global user.email "dpranjal366@gmail.com"')

    for i in range(1, num_commits + 1):
        now_ist, _ = get_ist_now()
        print(f"\n--- [Commit {i}/{num_commits}] at {now_ist.strftime('%I:%M:%S %p IST')} ---")
        
        # 1. Update telemetry & documentation
        update_status.update()
        
        # 2. Stage changes
        run_cmd("git add -A")
        
        # 3. Read dynamic commit message
        commit_msg = "chore(pulse): activity sync [skip ci]"
        if os.path.exists(".commit_msg"):
            with open(".commit_msg", "r", encoding="utf-8") as f:
                commit_msg = f.read().strip()
                
        # 4. Commit and push
        success, out = run_cmd(f'git commit -m "{commit_msg}"')
        if not success:
            print("Commit skipped (nothing to commit).")
        else:
            print(f"✅ Committed: {commit_msg}")
            
        push_success, push_out = run_cmd("git push origin main")
        if push_success:
            print(f"🚀 Pushed commit {i}/{num_commits} to GitHub main branch!")
        else:
            print(f"❌ Git push error: {push_out}")

        # 5. If more commits remain in this session, pause naturally
        if i < num_commits:
            if is_manual:
                pause_sec = 2  # Fast for manual dispatch testing
            else:
                # Realistic developer in-session break: 8 to 23 minutes
                pause_sec = random.randint(480, 1380)
                
            next_time = now_ist + timedelta(seconds=pause_sec)
            print(f"⏳ In-session iteration: sleeping {pause_sec // 60}m {pause_sec % 60}s...")
            print(f"🎯 Next commit scheduled at ~{next_time.strftime('%I:%M:%S %p IST')}")
            time.sleep(pause_sec)

    print("\n🏁 Developer Coding Session completed successfully.")

def main():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    
    # Cleanup skip flag
    if os.path.exists(SKIP_FLAG_FILE):
        os.remove(SKIP_FLAG_FILE)

    # 1. Manual Dispatch Bypass (Instant 1 or 2 commit test)
    if event_name == "workflow_dispatch":
        print("⚡ Manual workflow_dispatch detected: executing session immediately.")
        execute_session(num_commits=1, is_manual=True)
        return

    now_ist, now_utc = get_ist_now()
    today_str = now_ist.strftime("%Y-%m-%d")
    hour_utc = now_utc.hour

    history = load_history()
    target_today, planned_sessions = plan_day_blueprint(now_ist)
    commits_today = count_commits_today(today_str, history)

    current_idx, current_win = detect_current_window(hour_utc)
    win_name = current_win["name"] if current_win else f"UTC-Hour-{hour_utc}"

    print(f"📅 Date: {today_str} ({now_ist.strftime('%A')}) | Clock: {now_ist.strftime('%I:%M:%S %p IST')}")
    print(f"🎯 Daily Target: {target_today} commits (2–7 range) | Completed Today: {commits_today}")
    
    session_descriptions = []
    for s in planned_sessions:
        session_descriptions.append(f"{TIME_WINDOWS[s['window_idx']]['name']} ({s['commits']} commits)")
    print(f"🗺️ Today's Session Plan: {' + '.join(session_descriptions)}")

    # 2. Check if daily quota is already satisfied
    if commits_today >= target_today:
        print(f"✅ Daily target of {target_today} commits already met. Skipping to preserve organic rhythm.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 3. Check if current window matches any planned session
    matching_session = None
    for s in planned_sessions:
        if s["window_idx"] == current_idx:
            matching_session = s
            break

    if not matching_session:
        print(f"💤 Window '{win_name}' is not in today's active session schedule.")
        print("💤 Skipping gracefully to allow activity during planned session times.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 4. Check how many commits to make in this session
    remaining_needed = target_today - commits_today
    session_commits = min(matching_session["commits"], remaining_needed)
    
    if session_commits <= 0:
        print("✅ Session quota already satisfied.")
        with open(SKIP_FLAG_FILE, "w") as f:
            f.write("skip")
        return

    # 5. Session Start Initial Jitter (3m to 25m)
    # E.g., triggers around 17:30, starts session at 17:48!
    start_jitter = random.randint(180, 1500)
    start_time_ist = now_ist + timedelta(seconds=start_jitter)
    print(f"🎯 Session Start Time: {start_time_ist.strftime('%I:%M:%S %p IST')}")
    print(f"⏳ Sleeping {start_jitter // 60}m {start_jitter % 60}s before commencing session...")
    time.sleep(start_jitter)

    # 6. Execute the multi-commit session!
    execute_session(session_commits, is_manual=False)

if __name__ == "__main__":
    main()
