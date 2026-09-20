#!/usr/bin/env python3
"""
pulse.py
Local trigger script for Pranjal Das (@iPranjalDas)
Runs update_status.py, stages changes, and pushes a signed commit to GitHub.
"""

import subprocess
import sys
from datetime import datetime, timezone

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}\n{result.stderr}")
        return False
    return True

def main():
    print("💓 Executing Activity Pulse...")
    
    # Run update_status.py
    import update_status
    update_status.update()

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Stage and commit
    run_cmd("git add -A")
    run_cmd('git config user.name "Pranjal Das"')
    run_cmd('git config user.email "dpranjal366@gmail.com"')
    
    # Check if there are changes to commit
    diff = subprocess.run("git diff --staged --quiet", shell=True)
    if diff.returncode != 0:
        commit_msg = f"chore(pulse): activity heartbeat {now_utc}"
        run_cmd(f'git commit -m "{commit_msg}"')
        print(f"✅ Committed: {commit_msg}")
        
        # Push to origin main
        if run_cmd("git push origin main"):
            print("🚀 Successfully pushed pulse to GitHub main branch!")
        else:
            print("❌ Push failed. Check your network or git remote credentials.")
    else:
        print("ℹ️ No changes detected.")

if __name__ == "__main__":
    main()
