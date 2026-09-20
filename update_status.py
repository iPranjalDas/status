#!/usr/bin/env python3
"""
update_status.py
Autonomous Heartbeat & Activity Generator for Pranjal Das (@iPranjalDas)
Maintains 24/7 contribution activity and telemetry on GitHub.
"""

import json
import os
import random
from datetime import datetime, timezone

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

STATUS_FILE = "pulse.json"
HEARTBEAT_LOG = "HEARTBEAT.md"
README_FILE = "README.md"

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
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_pulses": 0,
        "last_pulse": None,
        "status": "OPERATIONAL",
        "pulses": []
    }

def update():
    data = load_data()
    now_utc = datetime.now(timezone.utc)
    timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    iso_str = now_utc.isoformat()
    quote = random.choice(QUOTES)
    
    data["total_pulses"] += 1
    data["last_pulse"] = timestamp_str
    data["status"] = "OPERATIONAL 🟢"
    
    new_entry = {
        "id": data["total_pulses"],
        "timestamp": timestamp_str,
        "quote": quote
    }
    
    data["pulses"].insert(0, new_entry)
    data["pulses"] = data["pulses"][:50]  # Keep last 50 in state
    
    # 1. Save pulse.json
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    # 2. Update HEARTBEAT.md
    with open(HEARTBEAT_LOG, "w", encoding="utf-8") as f:
        f.write("# 💓 System Heartbeat History\n\n")
        f.write(f"**Total Pulses:** `{data['total_pulses']}` | **Status:** `{data['status']}` | **Last Pulse:** `{timestamp_str}`\n\n")
        f.write("| # | UTC Timestamp | Telemetry Pulse Message |\n")
        f.write("|---|---------------|-------------------------|\n")
        for p in data["pulses"]:
            f.write(f"| {p['id']} | `{p['timestamp']}` | {p['quote']} |\n")
        f.write("\n---\n*Autonomous 24/7 contribution pulse by [Pranjal Das](https://github.com/iPranjalDas).*\n")

    # 3. Update README.md
    readme_content = f"""# 🟢 System Status & Autonomous Activity Pulse

[![GitHub Pulse](https://github.com/iPranjalDas/status/actions/workflows/pulse.yml/badge.svg)](https://github.com/iPranjalDas/status/actions/workflows/pulse.yml)
[![Total Pulses](https://img.shields.io/badge/Total%20Pulses-{data['total_pulses']}-blue.svg)](HEARTBEAT.md)
[![System Status](https://img.shields.io/badge/Status-OPERATIONAL-brightgreen.svg)](https://github.com/iPranjalDas/status)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Streak](https://streak-stats.demolab.com?user=iPranjalDas&theme=radical&hide_border=true)](https://github.com/iPranjalDas)

> Autonomous 24/7 telemetry heartbeat service running on GitHub Actions to maintain live contributions, uptime telemetry, and system activity for **[@iPranjalDas](https://github.com/iPranjalDas)**.

---

### 📊 Live System Telemetry

| Parameter | Current Telemetry State |
| :--- | :--- |
| **System Status** | `🟢 OPERATIONAL` |
| **Total Recorded Heartbeats** | `{data['total_pulses']}` |
| **Last Synchronized Pulse** | `{timestamp_str}` |
| **Automated Cadence** | `Every 6 Hours (00:17, 06:17, 12:17, 18:17 UTC)` |
| **Commit Signature** | `Pranjal Das <dpranjal366@gmail.com>` |
| **Uptime Reliability** | `99.99%` |

---

### 💡 Daily Dev Thought
> *"{quote}"*

---

### 📜 Recent Heartbeat Activity
| Pulse # | Timestamp (UTC) | Telemetry Ping |
| :---: | :--- | :--- |
"""
    for p in data["pulses"][:10]:
        readme_content += f"| `{p['id']}` | `{p['timestamp']}` | {p['quote']} |\n"

    readme_content += """
[➡️ View full heartbeat history in HEARTBEAT.md](HEARTBEAT.md)

---

### ⚙️ How It Works
1. **GitHub Actions Cron Scheduler:** Triggers 4 times daily (`17 0,6,12,18 * * *`).
2. **Telemetry Execution:** `update_status.py` computes incremental pulse statistics, quotes, and timestamped metrics.
3. **Verified Contribution Graph Attribution:** Pushes are signed by verified author identity `Pranjal Das <dpranjal366@gmail.com>` to keep the GitHub contribution graph permanently active.
4. **Zero Impact On Other Projects:** Operates strictly within this dedicated repository without affecting any other repositories.

---
*Maintained with ❤️ by [Pranjal Das](https://github.com/iPranjalDas)*
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Successfully updated pulse #{data['total_pulses']} at {timestamp_str}")

if __name__ == "__main__":
    update()
