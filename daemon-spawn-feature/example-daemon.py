#!/usr/bin/env python3
"""Minimal example daemon — JSON Lines on stdout, signal handling."""
import json, time, signal, os, sys
from datetime import datetime

RUNNING = True
def log(level, msg, **kw):
    print(json.dumps({"timestamp": datetime.utcnow().isoformat()+"Z",
                     "level": level, "message": msg, **kw}), flush=True)
signal.signal(signal.SIGTERM, lambda *a: globals().update(RUNNING=False))
signal.signal(signal.SIGINT, lambda *a: globals().update(RUNNING=False))

def main():
    interval = int(os.environ.get("INTERVAL_S", "10"))
    counter = 0
    log("info", f"Example daemon started", interval_s=interval, pid=os.getpid())
    while RUNNING:
        counter += 1
        log("info", f"Heartbeat #{counter}", counter=counter, uptime_s=counter*interval)
        try: time.sleep(interval)
        except KeyboardInterrupt: break
    log("info", "Example daemon exiting", total_heartbeats=counter)
    sys.exit(0)

if __name__ == "__main__": main()
