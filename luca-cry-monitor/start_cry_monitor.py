#!/usr/bin/env python3
"""Launches luca_cry_daemon.py as a background daemon, exits immediately."""
import os, sys, subprocess, time

daemon_script = os.path.join(os.path.dirname(__file__), "luca_cry_daemon.py")

# Fork and exit
pid = os.fork()
if pid > 0:
    print(f"✅ Cry monitor daemon starting (PID {pid})")
    print("   Events → /output/cry_events.json")
    print("   Status → /output/cry_status.json")
    print("   Log    → /output/cry_monitor.log")
    sys.exit(0)

# Child — exec the daemon
os.close(0)  # close stdin
os.open("/dev/null", os.O_RDONLY)  # stdin from null
os.execv(sys.executable, [sys.executable, daemon_script, "--daemon"])
