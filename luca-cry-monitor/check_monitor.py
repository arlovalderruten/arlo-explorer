import time, json, os
time.sleep(5)
log = "/output/cry_monitor.log"
status = "/output/cry_status.json"
events = "/output/cry_events.json"

print("=== cry_monitor.log ===")
if os.path.exists(log):
    print(open(log).read())
else:
    print("(not found)")

print("\n=== cry_status.json ===")
if os.path.exists(status):
    print(json.dumps(json.load(open(status)), indent=2))
else:
    print("(not found)")

print("\n=== cry_events.json ===")
if os.path.exists(events):
    print(json.dumps(json.load(open(events)), indent=2))
else:
    print("(not found)")
