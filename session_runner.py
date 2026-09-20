#!/usr/bin/env python3
"""
session_runner.py
Developer Session Clustering & Multi-Repository Distribution Engine
Simulates authentic human developer sessions across 3 active repositories:
- iPranjalDas/status      (Uptime pulse, status badges, system health)
- iPranjalDas/telemetry   (Performance benchmarks, latency metrics, diagnostics)
- iPranjalDas/daily-logs  (Engineering journal, developer notes, TIL checkpoints)

Features:
- Makes 2 to 6 commits in the SAME session with realistic coding intervals (8–23 min gaps)
- Distributes commits across the 3 repositories so activity looks completely natural
- Supports split days: e.g. Morning single commit (10:23) + Evening cluster (17:48, 18:09) or vice versa
- Daily volume: Strictly between 2 and 7 commits per day
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

import multi_repo_engine

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

def run_cmd_in(cwd, cmd):
    res = subprocess.run(cmd, shell=True, text=True, cwd=cwd, capture_output=True)
    if res.returncode != 0:
        print(f"Error in {cwd}: {cmd}\n{res.stderr}")
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

    seed = int(hashlib.sha256(f"blueprint-v4-{today_str}".encode()).hexdigest(), 16)
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
    if target == 2:
        session_sizes = [2] if rng.random() < 0.55 else [1, 1]
    else:
        if rng.random() < 0.45:
            session_sizes = [target]  # Cluster in one mega session
        else:
            if rng.random() < 0.65:
                s1 = 1
                s2 = target - 1
            else:
                s1 = rng.randint(2, target - 1)
                s2 = target - s1
            session_sizes = [s1, s2] if rng.random() < 0.5 else [s2, s1]

    # 3. Assign windows to sessions
    sessions = []
    if len(session_sizes) == 1:
        w_idx = rng.choice([0, 1, 2, 3]) if is_weekend else rng.choice([2, 3, 4])
        sessions.append({"window_idx": w_idx, "commits": session_sizes[0]})
    else:
        early_candidates = [0, 1, 2]
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
    Executes a developer coding session with realistic in-session pauses,
    distributing commits across status, telemetry, and daily-logs!
    """
    print(f"\n🚀 Starting Multi-Repo Developer Coding Session: {num_commits} commit(s) planned.")
    
    # 1. Ensure sibling repositories exist and are synced
    status_dir = os.path.dirname(os.path.abspath(__file__))
    token = os.environ.get("STATUS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    
    repo_paths = multi_repo_engine.ensure_sibling_repos(status_dir, token)
    repo_keys = ["status", "telemetry", "daily-logs"]

    # Shuffle or rotate target repos across the session commits
    session_repo_targets = []
    for i in range(num_commits):
        # Rotate through all 3 repos
        session_repo_targets.append(repo_keys[i % len(repo_keys)])
    random.shuffle(session_repo_targets)

    for i, target_repo in enumerate(session_repo_targets, start=1):
        now_ist, _ = get_ist_now()
        target_dir = repo_paths[target_repo]
        print(f"\n--- [Commit {i}/{num_commits}] Target: [{target_repo}] at {now_ist.strftime('%I:%M:%S %p IST')} ---")
        
        # 1. Update target repository content
        if target_repo == "status":
            commit_msg = multi_repo_engine.update_status_repo(target_dir)
        elif target_repo == "telemetry":
            commit_msg = multi_repo_engine.update_telemetry_repo(target_dir)
        elif target_repo == "daily-logs":
            commit_msg = multi_repo_engine.update_daily_logs_repo(target_dir)

        # 2. Stage, commit, and push in target repository
        run_cmd_in(target_dir, 'git config user.name "Pranjal Das"')
        run_cmd_in(target_dir, 'git config user.email "dpranjal366@gmail.com"')
        run_cmd_in(target_dir, "git add -A")
        
        c_ok, c_out = run_cmd_in(target_dir, f'git commit -m "{commit_msg}"')
        if not c_ok:
            print(f"Commit skipped in {target_repo} (nothing to commit).")
        else:
            print(f"✅ Committed to [{target_repo}]: {commit_msg}")
            
        p_ok, p_out = run_cmd_in(target_dir, "git push origin main")
        if p_ok:
            print(f"🚀 Pushed commit {i}/{num_commits} to [{target_repo}] on GitHub main branch!")
        else:
            print(f"❌ Git push error in [{target_repo}]: {p_out}")

        # 3. If more commits remain in this session, pause naturally
        if i < num_commits:
            if is_manual:
                pause_sec = 2  # Fast for manual dispatch testing
            else:
                pause_sec = random.randint(480, 1380) # 8 to 23 minutes
                
            next_time = now_ist + timedelta(seconds=pause_sec)
            print(f"⏳ In-session iteration: sleeping {pause_sec // 60}m {pause_sec % 60}s before next commit...")
            print(f"🎯 Next commit scheduled at ~{next_time.strftime('%I:%M:%S %p IST')}")
            time.sleep(pause_sec)

    print("\n🏁 Multi-Repository Developer Session completed successfully.")

def main():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    
    if os.path.exists(SKIP_FLAG_FILE):
        os.remove(SKIP_FLAG_FILE)

    # 1. Manual Dispatch Bypass (Instant 2-commit multi-repo test)
    if event_name == "workflow_dispatch":
        print("⚡ Manual workflow_dispatch detected: executing multi-repo session immediately.")
        execute_session(num_commits=2, is_manual=True)
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
    start_jitter = random.randint(180, 1500)
    start_time_ist = now_ist + timedelta(seconds=start_jitter)
    print(f"🎯 Session Start Time: {start_time_ist.strftime('%I:%M:%S %p IST')}")
    print(f"⏳ Sleeping {start_jitter // 60}m {start_jitter % 60}s before commencing session...")
    time.sleep(start_jitter)

    # 6. Execute the multi-commit multi-repo session!
    execute_session(session_commits, is_manual=False)

if __name__ == "__main__":
    main()
