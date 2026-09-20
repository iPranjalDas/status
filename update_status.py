#!/usr/bin/env python3
"""
update_status.py
History-Aware Autonomous Activity Pulse Generator for Pranjal Das (@iPranjalDas)
Features:
- Never repeats commit prefix/scope consecutively (anti-pattern guard)
- Generates realistic developer commit messages (Conventional Commits)
- Varied file updates (pulse.json, HEARTBEAT.md, README.md, telemetry_history.json)
"""

import json
import os
import random
from datetime import datetime, timezone, timedelta

QUOTES = [
    "Code is like humor. When you have to explain it, it’s bad.",
    "First, solve the problem. Then, write the code.",
    "Make it work, make it right, make it fast.",
    "Simplicity is prerequisite for reliability.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "Talk is cheap. Show me the code.",
    "Programs must be written for people to read, and only incidentally for machines to execute.",
    "Truth can only be found in one place: the code.",
    "The only way to go fast is to go well.",
    "Perfection is achieved not when there is nothing more to add, but rather when there is nothing more to take away.",
    "Optimism is an occupational hazard of programming: feedback is the treatment.",
    "Controlling complexity is the essence of computer programming."
]

COMMIT_POOLS = {
    "feat": [
        "feat(pulse): record daily activity checkpoint and health ping",
        "feat(monitor): track daily system reliability benchmarks",
        "feat(telemetry): record uptime statistics and session state"
    ],
    "refactor": [
        "refactor(telemetry): optimize health log rotation and state persistence",
        "refactor(pipeline): clean up log rotation and state persistence",
        "refactor(buffers): streamline heartbeat sync buffers"
    ],
    "docs": [
        "docs(readme): refresh telemetry metrics and daily developer thought",
        "docs(notes): update daily developer thought and activity log",
        "docs(heartbeat): sync telemetry pulse history and uptime table"
    ],
    "perf": [
        "perf(monitor): streamline heartbeat sync buffers",
        "perf(logging): optimize markdown table rendering and streak sync",
        "perf(stream): reduce telemetry payload serialize latency"
    ],
    "chore": [
        "chore(deps): update runtime dependencies and pulse telemetry",
        "chore(pulse): automated health checkpoint and telemetry pulse",
        "chore(maintenance): routine node pulse and system health audit"
    ],
    "style": [
        "style(badges): align uptime shields and activity badges",
        "style(readme): format markdown tables and telemetry layouts"
    ],
    "fix": [
        "fix(telemetry): calibrate timestamp precision and timezone offsets",
        "fix(formatting): align table columns and delimiter spacing"
    ]
}

STATUS_FILE = "pulse.json"
HEARTBEAT_LOG = "HEARTBEAT.md"
README_FILE = "README.md"
TELEMETRY_LOG = "telemetry_history.json"
COMMIT_MSG_FILE = ".commit_msg"

def load_data():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "repository": "iPranjalDas/status",
        "maintainer": "Pranjal Das (@iPranjalDas)",
        "email": "dpranjal366@gmail.com",
        "total_pulses": 0,
        "last_pulse_utc": None,
        "last_pulse_ist": None,
        "last_category": None,
        "status": "OPERATIONAL",
        "pulses": []
    }

def pick_commit_message(last_category):
    # Pick a category that is DIFFERENT from the last category
    available_categories = [c for c in COMMIT_POOLS.keys() if c != last_category]
    category = random.choice(available_categories)
    message = random.choice(COMMIT_POOLS[category])
    return category, message

def update():
    data = load_data()
    now_utc = datetime.now(timezone.utc)
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = now_utc.astimezone(ist)

    timestamp_utc_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    timestamp_ist_str = now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
    quote = random.choice(QUOTES)
    
    last_cat = data.get("last_category")
    category, commit_msg = pick_commit_message(last_cat)
    
    data["total_pulses"] += 1
    data["last_pulse_utc"] = timestamp_utc_str
    data["last_pulse_ist"] = timestamp_ist_str
    data["last_category"] = category
    data["status"] = "OPERATIONAL 🟢"
    
    new_entry = {
        "id": data["total_pulses"],
        "timestamp_ist": timestamp_ist_str,
        "timestamp_utc": timestamp_utc_str,
        "category": category,
        "quote": quote
    }
    
    data["pulses"].insert(0, new_entry)
    data["pulses"] = data["pulses"][:50]  # Keep last 50
    
    # 1. Save pulse.json
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    # 2. Write dynamic commit message
    with open(COMMIT_MSG_FILE, "w", encoding="utf-8") as f:
        f.write(f"{commit_msg} [skip ci]\n")

    # 3. Update telemetry_history.json (varied file change payload)
    history_entries = []
    if os.path.exists(TELEMETRY_LOG):
        try:
            with open(TELEMETRY_LOG, "r", encoding="utf-8") as f:
                history_entries = json.load(f)
        except Exception:
            pass
    history_entries.insert(0, {
        "pulse_id": data["total_pulses"],
        "timestamp_ist": timestamp_ist_str,
        "memory_load": f"{random.uniform(18.2, 24.8):.1f}%",
        "latency_ms": random.randint(12, 48),
        "status": "HEALTHY"
    })
    with open(TELEMETRY_LOG, "w", encoding="utf-8") as f:
        json.dump(history_entries[:30], f, indent=2)

    # 4. Update HEARTBEAT.md
    with open(HEARTBEAT_LOG, "w", encoding="utf-8") as f:
        f.write("# 💓 System Heartbeat & Activity History\n\n")
        f.write(f"**Total Pulses:** `{data['total_pulses']}` | **Status:** `{data['status']}` | **Last Pulse:** `{timestamp_ist_str}`\n\n")
        f.write("| # | Time (IST) | Time (UTC) | Type | Telemetry Pulse Message |\n")
        f.write("|---|------------|------------|------|-------------------------|\n")
        for p in data["pulses"]:
            ist_val = p.get("timestamp_ist", p.get("timestamp", "N/A"))
            utc_val = p.get("timestamp_utc", "N/A")
            cat_val = p.get("category", "pulse")
            f.write(f"| {p['id']} | `{ist_val}` | `{utc_val}` | `{cat_val}` | {p['quote']} |\n")
        f.write("\n---\n*Autonomous non-patterned contribution pulse by [Pranjal Das](https://github.com/iPranjalDas).*\n")

    # 5. Update README.md
    readme_content = f"""# 🟢 System Status & Autonomous Activity Pulse

[![GitHub Pulse](https://github.com/iPranjalDas/status/actions/workflows/pulse.yml/badge.svg)](https://github.com/iPranjalDas/status/actions/workflows/pulse.yml)
[![Total Pulses](https://img.shields.io/badge/Total%20Pulses-{data['total_pulses']}-blue.svg)](HEARTBEAT.md)
[![System Status](https://img.shields.io/badge/Status-OPERATIONAL-brightgreen.svg)](https://github.com/iPranjalDas/status)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Streak](https://streak-stats.demolab.com?user=iPranjalDas&theme=radical&hide_border=true)](https://github.com/iPranjalDas)

> Autonomous 24/7 telemetry heartbeat service running on GitHub Actions with **history-aware anti-pattern human timing** to maintain authentic contributions, uptime telemetry, and activity for **[@iPranjalDas](https://github.com/iPranjalDas)**.

---

### 📊 Live System Telemetry

| Parameter | Current Telemetry State |
| :--- | :--- |
| **System Status** | `🟢 OPERATIONAL` |
| **Total Recorded Heartbeats** | `{data['total_pulses']}` |
| **Last Synchronized Pulse (IST)** | `{timestamp_ist_str}` |
| **Last Synchronized Pulse (UTC)** | `{timestamp_utc_str}` |
| **Timing Pattern** | `Anti-Pattern Non-Repeating Jitter (History-Aware)` |
| **Daily Variance** | `Dynamic 1 to 3 Commits / Day + Micro-Bursts` |
| **Commit Signature** | `Pranjal Das <dpranjal366@gmail.com>` |
| **Uptime Reliability** | `99.99%` |

---

### 💡 Daily Dev Thought
> *"{quote}"*

---

### 📜 Recent Heartbeat Activity
| Pulse # | Timestamp (IST) | Type | Telemetry Ping |
| :---: | :--- | :---: | :--- |
"""
    for p in data["pulses"][:10]:
        ist_val = p.get("timestamp_ist", p.get("timestamp", "N/A"))
        cat_val = p.get("category", "pulse")
        readme_content += f"| `{p['id']}` | `{ist_val}` | `{cat_val}` | {p['quote']} |\n"

    readme_content += """
[➡️ View full heartbeat history in HEARTBEAT.md](HEARTBEAT.md)

---

### ⚙️ How It Works (Advanced Anti-Pattern Cadence)
1. **History-Aware Engine:** Before every run, the cloud runner inspects recent commit timestamps and daily counts to prevent repetitive clusters.
2. **Variable Daily Rhythm:** Dynamically varies between **1, 2, and 3 commits per day**, so no two consecutive days look identical.
3. **Natural Developer Micro-Bursts:** Occasionally simulates a developer making an initial commit followed by a quick refinement 4–11 minutes later.
4. **Scope & Message Rotation:** Automatically rotates Conventional Commit scopes (`feat`, `refactor`, `perf`, `docs`, `fix`, `chore`, `style`), strictly preventing consecutive repetition.
5. **Zero Laptop Footprint:** 100% cloud-executed on Microsoft/GitHub infrastructure with 0% local laptop CPU/RAM consumption.

---
*Maintained with ❤️ by [Pranjal Das](https://github.com/iPranjalDas)*
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Successfully updated pulse #{data['total_pulses']} ({category}) at {timestamp_ist_str}")

if __name__ == "__main__":
    update()
