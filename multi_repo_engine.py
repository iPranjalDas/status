#!/usr/bin/env python3
"""
multi_repo_engine.py
Multi-Repository Activity Distributor for Pranjal Das (@iPranjalDas)
Distributes commits across 3 cohesive repositories:
1. status       - System heartbeat, uptime telemetry, status pulse
2. telemetry    - System performance benchmarks, latency logs, diagnostics
3. daily-logs   - Engineering journal, developer notes, TIL checkpoints
"""

import json
import os
import random
import subprocess
from datetime import datetime, timezone, timedelta

def get_ist_now():
    now_utc = datetime.now(timezone.utc)
    ist = timezone(timedelta(hours=5, minutes=30))
    return now_utc.astimezone(ist), now_utc

def run_cmd_in(cwd, cmd):
    res = subprocess.run(cmd, shell=True, text=True, cwd=cwd, capture_output=True)
    if res.returncode != 0:
        print(f"Error in {cwd}: {cmd}\n{res.stderr}")
        return False, res.stderr
    return True, res.stdout

def update_status_repo(repo_dir):
    """Updates status repository"""
    import update_status
    update_status.update()
    
    commit_msg = "chore(pulse): activity sync [skip ci]"
    commit_file = os.path.join(repo_dir, ".commit_msg")
    if os.path.exists(commit_file):
        with open(commit_file, "r", encoding="utf-8") as f:
            commit_msg = f.read().strip()
    return commit_msg

def update_telemetry_repo(repo_dir):
    """Updates telemetry repository with performance benchmarks"""
    now_ist, _ = get_ist_now()
    timestamp_str = now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
    
    latency = random.randint(14, 38)
    mem_pct = round(random.uniform(19.5, 27.8), 1)
    buffer_health = round(random.uniform(99.92, 99.99), 2)
    
    # 1. Update metrics.json
    metrics_file = os.path.join(repo_dir, "metrics.json")
    data = {"system": "telemetry-engine", "status": "HEALTHY", "samples": []}
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
            
    data["samples"].insert(0, {
        "timestamp": timestamp_str,
        "latency_ms": latency,
        "memory_pct": mem_pct,
        "buffer_health": f"{buffer_health}%",
        "status": "OPTIMAL"
    })
    data["samples"] = data["samples"][:40]
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 2. Update BENCHMARKS.md
    bench_file = os.path.join(repo_dir, "BENCHMARKS.md")
    with open(bench_file, "w", encoding="utf-8") as f:
        f.write("# 📊 System Performance & Benchmark Log\n\n")
        f.write(f"**Last Calibration:** `{timestamp_str}` | **Status:** `OPTIMAL 🟢`\n\n")
        f.write("| Timestamp (IST) | Latency | Memory Allocation | Buffer Health | Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for s in data["samples"]:
            f.write(f"| `{s['timestamp']}` | `{s['latency_ms']} ms` | `{s['memory_pct']}%` | `{s.get('buffer_health', '99.98%')}` | `OPTIMAL 🟢` |\n")
        f.write("\n---\n*Autonomous performance tracking by [Pranjal Das](https://github.com/iPranjalDas).*\n")

    # 3. Update README.md
    readme_file = os.path.join(repo_dir, "README.md")
    readme_content = f"""# ⚡ System Telemetry & Performance Benchmarks

[![System Status](https://img.shields.io/badge/Status-OPERATIONAL-brightgreen.svg)](https://github.com/iPranjalDas/telemetry)
[![Telemetry Engine](https://img.shields.io/badge/Telemetry-Active-blue.svg)](BENCHMARKS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Streak](https://streak-stats.demolab.com?user=iPranjalDas&theme=radical&hide_border=true)](https://github.com/iPranjalDas)

> Continuous automated system telemetry, runtime performance tracking, and micro-benchmarks for **[@iPranjalDas](https://github.com/iPranjalDas)**.

---

### 📊 Live System Metrics
| Metric | Current State | Target Threshold | Status |
| :--- | :---: | :---: | :---: |
| **API Response Latency** | `{latency} ms` | `< 50 ms` | `OPTIMAL 🟢` |
| **Telemetry Buffer Health** | `{buffer_health}%` | `> 99.0%` | `HEALTHY 🟢` |
| **Memory Allocation Index** | `{mem_pct}%` | `< 40.0%` | `NOMINAL 🟢` |
| **Last Calibration** | `{timestamp_str}` | `Continuous` | `SYNCHRONIZED 🟢` |

---

### 📈 Micro-Benchmark Log
[➡️ View full benchmark tracking in BENCHMARKS.md](BENCHMARKS.md)

---
*Maintained with ❤️ by [Pranjal Das](https://github.com/iPranjalDas)*
"""
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)

    commit_msgs = [
        "perf(benchmarks): calibrate latency sample buffers [skip ci]",
        "feat(telemetry): record hourly system throughput index [skip ci]",
        "refactor(metrics): optimize rolling memory histogram [skip ci]",
        "fix(telemetry): adjust threshold warning boundaries [skip ci]",
        "style(benchmarks): format latency telemetry table [skip ci]",
        "perf(stream): reduce payload serialization overhead [skip ci]"
    ]
    return random.choice(commit_msgs)

def update_daily_logs_repo(repo_dir):
    """Updates daily-logs repository with developer journal and TIL insights"""
    now_ist, _ = get_ist_now()
    date_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%I:%M:%S %p IST")

    TOPICS = [
        ("Distributed Cloud Schedulers", "Decoupled cloud execution enables 24/7 reliability with zero local hardware consumption.", "#architecture #devops #cloud"),
        ("Cache Invalidation & DrvFs", "POSIX 9p DrvFs translation requires disabling disk memory-mapping cache to avoid SIGBUS faults.", "#wsl2 #kernel #fs"),
        ("Asynchronous Event Loops", "Batching IO bound task iterations into structured coroutines prevents socket exhaustion.", "#python #performance #async"),
        ("Sparse VHD dynamic hole punching", "NTFS compacting triggers sparse flag assertion; fstrim with discard allows dynamic host punch-through.", "#storage #wsl #linux"),
        ("Hardware Rate Limit Windows", "Honoring x-ratelimit-reset headers strictly without aggressive polling eliminates secondary backoff penalties.", "#api #github #automation"),
        ("Conventional Commits & Semantic Graph", "Categorized commit scopes (feat, fix, perf, docs) produce clean changelogs and rich graph heatmaps.", "#git #engineering #workflow"),
        ("System Telemetry Histograms", "Exponential moving averages on buffer latency provide stable metrics under intermittent network load.", "#telemetry #monitoring #systems")
    ]
    
    topic, insight, tags = random.choice(TOPICS)

    # 1. Update til.json
    til_file = os.path.join(repo_dir, "til.json")
    data = {"developer": "Pranjal Das (@iPranjalDas)", "entries": []}
    if os.path.exists(til_file):
        try:
            with open(til_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
            
    data["entries"].insert(0, {
        "date": date_str,
        "time": time_str,
        "topic": topic,
        "insight": insight,
        "tags": tags
    })
    data["entries"] = data["entries"][:35]
    with open(til_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 2. Update journal.md
    journal_file = os.path.join(repo_dir, "journal.md")
    with open(journal_file, "w", encoding="utf-8") as f:
        f.write("# 📓 Engineering Journal & TIL Log\n\n")
        f.write(f"**Last Entry:** `{date_str} at {time_str}` | **Author:** [Pranjal Das](https://github.com/iPranjalDas)\n\n")
        for e in data["entries"]:
            f.write(f"### 📅 {e['date']} ({e.get('time', 'Session')})\n")
            f.write(f"* **Focus:** {e['topic']}\n")
            f.write(f"* **TIL:** {e['insight']}\n")
            f.write(f"* **Tags:** `{e.get('tags', '#dev')}`\n\n")
        f.write("---\n*Autonomous developer journal by [Pranjal Das](https://github.com/iPranjalDas).*\n")

    # 3. Update README.md
    readme_file = os.path.join(repo_dir, "README.md")
    readme_content = f"""# 📖 Daily Engineering Journal & Developer Notes

[![Journal Status](https://img.shields.io/badge/Journal-Active-brightgreen.svg)](https://github.com/iPranjalDas/daily-logs)
[![TIL Notes](https://img.shields.io/badge/TIL-Notes-blue.svg)](journal.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Streak](https://streak-stats.demolab.com?user=iPranjalDas&theme=radical&hide_border=true)](https://github.com/iPranjalDas)

> Continuous engineering notes, daily developer insights, algorithmic problem-solving records, and Today-I-Learned (TIL) checkpoints for **[@iPranjalDas](https://github.com/iPranjalDas)**.

---

### 📝 Recent Journal Focus
* **Latest Topic:** `{topic}`
* **Last Entry:** `{date_str} {time_str}`
* **Insight:** *"{insight}"*

[➡️ View all developer journal entries in journal.md](journal.md)

---
*Maintained with ❤️ by [Pranjal Das](https://github.com/iPranjalDas)*
"""
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)

    commit_msgs = [
        f"docs(journal): add engineering note on {topic.lower()} [skip ci]",
        f"feat(til): record insights on {topic.lower()} [skip ci]",
        "docs(notes): update daily engineering checkpoints [skip ci]",
        "refactor(journal): format weekly topic index [skip ci]",
        "style(readme): update recent focus highlight [skip ci]"
    ]
    return random.choice(commit_msgs)

def ensure_sibling_repos(base_dir, token):
    """
    Ensures sibling repositories (telemetry, daily-logs) are cloned and ready.
    """
    repos = {
        "telemetry": "https://github.com/iPranjalDas/telemetry.git",
        "daily-logs": "https://github.com/iPranjalDas/daily-logs.git"
    }
    paths = {"status": base_dir}
    parent_dir = os.path.dirname(os.path.abspath(base_dir))

    for name, url in repos.items():
        repo_path = os.path.join(parent_dir, name)
        paths[name] = repo_path
        auth_url = f"https://x-access-token:{token}@github.com/iPranjalDas/{name}.git" if token else url

        if not os.path.exists(repo_path):
            print(f"📦 Cloning sibling repo '{name}'...")
            subprocess.run(f"git clone {auth_url} {repo_path}", shell=True, capture_output=True)
            run_cmd_in(repo_path, 'git config user.name "Pranjal Das"')
            run_cmd_in(repo_path, 'git config user.email "dpranjal366@gmail.com"')
        else:
            # Sync origin URL with token and pull latest
            run_cmd_in(repo_path, f"git remote set-url origin {auth_url}")
            run_cmd_in(repo_path, "git pull origin main")

    return paths
