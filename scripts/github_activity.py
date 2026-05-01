#!/usr/bin/env python3
"""
GitHub Activity Feed - What's happening in interesting repos
"""

import json
import urllib.request
from datetime import datetime

# Interesting repos to watch
REPOS = [
    "microsoft/vscode",
    "facebook/react",
    "rust-lang/rust",
    "torvalds/linux",
    "openai/gym",
    "tensorflow/tensorflow",
    "denoland/deno",
    "vitejs/vite",
    "vercel/next.js",
    "tailwindlabs/tailwindcss"
]

def get_repo_activity(repo):
    """Get recent activity from a repo"""
    try:
        url = f"https://api.github.com/repos/{repo}/events"
        req = urllib.request.Request(url, headers={'User-Agent': 'GitHubActivity/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            events = json.loads(resp.read())
            
            activity = []
            for event in events[:5]:
                activity.append({
                    'type': event.get('type', ''),
                    'actor': event.get('actor', {}).get('login', 'unknown'),
                    'repo': event.get('repo', {}).get('name', ''),
                    'time': event.get('created_at', '')[:16]
                })
            return activity
    except Exception as e:
        return []

def main():
    print("=" * 60)
    print("👾 GITHUB ACTIVITY FEED")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    all_events = []
    
    print("\n📥 Fetching activity from interesting repos...")
    
    for repo in REPOS:
        print(f"   Checking {repo}...", end=" ")
        activity = get_repo_activity(repo)
        if activity:
            print(f"✅ {len(activity)} events")
            all_events.extend(activity[:3])
        else:
            print("⚠️  rate limited or error")
    
    # Sort by time
    all_events.sort(key=lambda x: x['time'], reverse=True)
    
    # Group by type
    event_types = {}
    for event in all_events:
        t = event['type']
        if t not in event_types:
            event_types[t] = []
        event_types[t].append(event)
    
    print("\n" + "=" * 60)
    print("📊 ACTIVITY BY TYPE")
    print("=" * 60)
    
    type_names = {
        'PushEvent': '📝 Push',
        'PullRequestEvent': '🔀 PR',
        'IssuesEvent': '🐛 Issue',
        'WatchEvent': '⭐ Star',
        'ForkEvent': '🍴 Fork',
        'CreateEvent': '✨ Create',
        'DeleteEvent': '🗑️ Delete',
        'ReleaseEvent': '📦 Release',
        'IssueCommentEvent': '💬 Comment',
        'PullRequestReviewEvent': '👀 Review'
    }
    
    for etype, events in event_types.items():
        icon = type_names.get(etype, '❓')
        print(f"\n   {icon} {etype}: {len(events)} events")
        
        for event in events[:2]:
            repo = event['repo'].split('/')[-1]
            actor = event['actor']
            time = event['time'][11:]
            print(f"      • {actor} → {repo} at {time}")
    
    # Most active repos
    print("\n" + "=" * 60)
    print("🔥 MOST ACTIVE REPOS (in last 24h)")
    print("=" * 60)
    
    from collections import Counter
    repo_counts = Counter(e['repo'] for e in all_events)
    
    for repo, count in repo_counts.most_common(5):
        print(f"   {repo}: {count} events")
    
    # Save
    result = {
        'timestamp': datetime.now().isoformat(),
        'events': all_events[:30],
        'by_type': {k: len(v) for k, v in event_types.items()},
        'repos_checked': len(REPOS)
    }
    
    with open('/output/github_activity.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Saved to /output/github_activity.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()