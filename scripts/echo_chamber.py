#!/usr/bin/env python3
"""
Echo Chamber Detector - Analyzes if your feeds are creating an echo chamber
Compares your HN/Reddit consumption to global Reddit trending
"""

import json
import urllib.request
from datetime import datetime
from collections import Counter

def get_global_trending():
    """Get truly global/trending content"""
    try:
        url = "https://www.reddit.com/r/popular/hot.json?limit=25"
        req = urllib.request.Request(url, headers={'User-Agent': 'EchoChamber/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            posts = []
            for child in data.get('data', {}).get('children', [])[:25]:
                post = child.get('data', {})
                posts.append({
                    'subreddit': post.get('subreddit', 'unknown'),
                    'title': post.get('title', ''),
                    'score': post.get('score', 0)
                })
            return posts
    except Exception as e:
        return []

def get_worldnews():
    """Get world news content"""
    try:
        url = "https://www.reddit.com/r/worldnews/hot.json?limit=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'EchoChamber/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            posts = []
            for child in data.get('data', {}).get('children', [])[:15]:
                post = child.get('data', {})
                posts.append({
                    'subreddit': post.get('subreddit', 'unknown'),
                    'title': post.get('title', ''),
                    'score': post.get('score', 0)
                })
            return posts
    except Exception as e:
        return []

def categorize_content(posts):
    """Simple categorization of content"""
    categories = Counter()
    topics = Counter()
    
    keywords = {
        'politics': ['trump', 'biden', 'congress', 'senate', 'election', 'vote', 'democrat', 'republican'],
        'world': ['war', 'ukraine', 'russia', 'china', 'iran', 'israel', 'military', 'conflict'],
        'tech': ['ai', 'openai', 'google', 'apple', 'microsoft', 'startup', 'software', 'code'],
        'finance': ['stock', 'market', 'crypto', 'bitcoin', 'money', 'invest', 'economy'],
        'science': ['space', 'nasa', 'research', 'study', 'science', 'discover'],
        'culture': ['music', 'movie', 'sport', 'social', 'culture', 'life']
    }
    
    for post in posts:
        title = post.get('title', '').lower()
        found = False
        for cat, words in keywords.items():
            if any(w in title for w in words):
                categories[cat] += post.get('score', 1)
                topics[cat] += 1
                found = True
                break
        if not found:
            categories['other'] += post.get('score', 1)
            topics['other'] += 1
    
    return categories, topics

def analyze_echo_chamber():
    print("=" * 60)
    print("🔊 ECHO CHAMBER DETECTOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    print("\n📥 Fetching global Reddit trends...")
    global_posts = get_global_trending()
    world_posts = get_worldnews()
    
    print(f"   Collected {len(global_posts)} global + {len(world_posts)} worldnews")
    
    # Categorize
    print("\n🔍 Analyzing content distribution...")
    
    global_cats, global_topics = categorize_content(global_posts)
    world_cats, world_topics = categorize_content(world_posts)
    
    print("\n📊 GLOBAL REDDIT (r/popular):")
    print("-" * 40)
    total = sum(global_cats.values())
    for cat, score in global_cats.most_common():
        pct = (score / total * 100) if total else 0
        count = global_topics[cat]
        bar = "█" * int(pct / 5)
        print(f"   {cat:10} {bar:20} {pct:5.1f}% ({count} posts)")
    
    print("\n📊 WORLD NEWS (r/worldnews):")
    print("-" * 40)
    total = sum(world_cats.values())
    for cat, score in world_cats.most_common():
        pct = (score / total * 100) if total else 0
        count = world_topics[cat]
        bar = "█" * int(pct / 5)
        print(f"   {cat:10} {bar:20} {pct:5.1f}% ({count} posts)")
    
    # Echo chamber analysis
    print("\n" + "=" * 60)
    print("🎯 ECHO CHAMBER ANALYSIS")
    print("=" * 60)
    
    # Compare top categories
    top_global = global_cats.most_common(3)
    top_world = world_cats.most_common(3)
    
    print(f"\n   Global top 3: {[c[0] for c in top_global]}")
    print(f"   WorldNews top 3: {[c[0] for c in top_world]}")
    
    # Check overlap
    global_set = {c[0] for c in top_global}
    world_set = {c[0] for c in top_world}
    overlap = global_set & world_set
    
    if len(overlap) >= 2:
        echo_score = 70
        echo_label = "HIGH - Heavy overlap between your feeds"
    elif len(overlap) == 1:
        echo_score = 45
        echo_label = "MEDIUM - Some common content, some divergence"
    else:
        echo_score = 20
        echo_label = "LOW - Your feeds show diverse content"
    
    print(f"\n   📈 Echo Score: {echo_score}/100")
    print(f"   📝 {echo_label}")
    
    # Specific insights
    if 'world' in global_set and 'world' in world_set:
        print("\n   ⚠️  WARNING: Both feeds heavily focused on conflict/war")
        print("   💡 Consider: Add tech/science feeds for balance")
    
    if 'tech' not in global_set and 'tech' not in world_set:
        print("\n   💡 TIP: Tech content is underrepresented in your feeds")
    
    # Save analysis
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'echo_score': echo_score,
        'echo_label': echo_label,
        'global_categories': dict(global_cats.most_common()),
        'worldnews_categories': dict(world_cats.most_common()),
        'top_global': [c[0] for c in top_global],
        'top_world': [c[0] for c in top_world]
    }
    
    with open('/output/echo_chamber_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print("\n✅ Analysis saved to /output/echo_chamber_analysis.json")

if __name__ == "__main__":
    analyze_echo_chamber()