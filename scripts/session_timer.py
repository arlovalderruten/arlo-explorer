#!/usr/bin/env python3
"""
Session Timer - Track time across context compactions
Uses real system time to maintain accurate timing regardless of context state
"""
import json
from datetime import datetime
from pathlib import Path

SESSION_FILE = "/output/session_timer.json"

def get_timestamp():
    return datetime.now().isoformat()

def get_elapsed_minutes(start_iso):
    """Calculate minutes elapsed since start time"""
    start = datetime.fromisoformat(start_iso)
    elapsed = datetime.now() - start
    return int(elapsed.total_seconds() / 60)

def log_event(event_type, description):
    """Log an event with timestamp"""
    data = load_session()
    
    # Add event
    data["events"].append({
        "type": event_type,
        "description": description,
        "timestamp": get_timestamp()
    })
    
    save_session(data)
    return data

def log_session_start():
    """Initialize or update session start time"""
    data = load_session()
    if data["session_start"] is None:
        data["session_start"] = get_timestamp()
        save_session(data)
    return data

def log_context_compaction():
    """Record when context compacts"""
    return log_event("compaction", "Context was compacted")

def log_collaborator_leave():
    """Record when Camilo leaves"""
    return log_event("departure", "Collaborator left")

def log_collaborator_return():
    """Record when Camilo returns"""
    return log_event("return", "Collaborator returned")

def get_time_since_last(event_type=None):
    """Get minutes since last event of type, or since session start"""
    data = load_session()
    
    if data["session_start"] is None:
        return "No session start recorded"
    
    start = datetime.fromisoformat(data["session_start"])
    elapsed = datetime.now() - start
    minutes = int(elapsed.total_seconds() / 60)
    hours = minutes // 60
    mins = minutes % 60
    
    if event_type:
        for event in reversed(data["events"]):
            if event["type"] == event_type:
                event_time = datetime.fromisoformat(event["timestamp"])
                since = datetime.now() - event_time
                m = int(since.total_seconds() / 60)
                h = m // 60
                mi = m % 60
                if h > 0:
                    return f"{h}h {mi}m ago ({event['description']})"
                else:
                    return f"{m}m ago ({event['description']})"
    
    if hours > 0:
        return f"{hours}h {mins}m total"
    else:
        return f"{mins}m total"

def load_session():
    """Load session data"""
    try:
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"session_start": None, "events": []}

def save_session(data):
    """Save session data"""
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def status():
    """Print current session status"""
    data = load_session()
    
    print("=" * 60)
    print("⏱️  SESSION TIMER STATUS")
    print(f"   {get_timestamp()}")
    print("=" * 60)
    
    # Session start
    if data["session_start"]:
        elapsed = get_elapsed_minutes(data["session_start"])
        hours = elapsed // 60
        mins = elapsed % 60
        print(f"\n📍 Session started: {data['session_start']}")
        print(f"   Elapsed: {hours}h {mins}m ({elapsed} minutes)")
    else:
        print("\n📍 Session not started")
    
    # Last events
    if data["events"]:
        print("\n📋 Recent Events:")
        for event in data["events"][-5:]:
            print(f"   • {event['timestamp']} - {event['description']}")
    
    # Time since last
    print(f"\n⏰ {get_time_since_last()}")
    
    print("=" * 60)
    
    return data

def main():
    import sys
    
    if len(sys.argv) < 2:
        status()
        return
    
    action = sys.argv[1].lower()
    
    if action == "start":
        data = log_session_start()
        print(f"✅ Session started at {data['session_start']}")
    
    elif action == "leave":
        data = log_collaborator_leave()
        print("✅ Logged: Collaborator departed")
    
    elif action == "return":
        data = log_collaborator_return()
        print("✅ Logged: Collaborator returned")
    
    elif action == "compaction":
        data = log_context_compaction()
        print("✅ Logged: Context compaction")
    
    elif action == "status":
        status()
    
    elif action == "elapsed":
        print(get_time_since_last())
    
    elif action == "event":
        if len(sys.argv) >= 4:
            event_type = sys.argv[2]
            description = sys.argv[3]
            log_event(event_type, description)
            print(f"✅ Logged: {event_type} - {description}")
        else:
            print("Usage: session_timer.py event <type> <description>")
    
    else:
        print(f"Unknown action: {action}")
        print("Options: start, leave, return, compaction, status, elapsed, event")

if __name__ == "__main__":
    main()