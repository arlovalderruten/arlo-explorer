#!/usr/bin/env python3
"""
Perspective Aggregator - Shows how different communities cover the same topic
"""

import json
import urllib.request
from datetime import datetime
from collections import Counter

def fetch_topic_coverage(topic):
    """Fetch how different sources cover a topic"""
    communities = {
        'r/technology': 'https://www.reddit.com/r/technology/hot.json?limit=10',
        'r/politics': 'https://www.reddit.com/r/politics/hot.json?limit=10',
        'r/worldnews': 'https://www.reddit.com/r/worldnews/hot.json?limit=10',
        'r/news': 'https://www.reddit.com/r/news/hot.json?limit=10',
        'r/science': 'https://www.reddit.com/r/science/hot.json?limit=10',
    }
    
    print(f"\n📥 Searching for: '{topic}'")
    print("-" * 50)
    
    coverage = []
    
    for community, url in communities.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PerspectiveBot/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                
            for child in data.get('data', {}).get('children', [])[:10]:
                post = child.get('data', {})
                title = post.get('title', '').lower()
                if topic.lower() in title:
                    coverage.append({
                        'title': post.get('title', ''),
                        'score': post.get('score', 0),
                        'community': community
                    })
            
            found = [c for c in coverage if c['community'] == community]
            if found:
                print(f"\n   📍 {community}: {len(found)} posts")
                for post in found[:3]:
                    print(f"      • {post['title'][:60]}... ({post['score']} pts)")
                    
        except Exception as e:
            print(f"   ❌ {community}: error")
    
    return coverage

def analyze_perspectives(coverage):
    """Analyze spin and emotional language"""
    emotional_words = {
        'negative': ['disaster', 'crisis', 'catastrophe', 'nightmare', 'horror', 'devastating', 'tragic', 'attack', 'threat', 'danger'],
        'positive': ['breakthrough', 'success', 'amazing', 'hope', 'victory', 'brilliant', 'incredible', 'progress', 'achievement'],
        'alarming': ['warning', 'urgent', 'critical', 'emergency', 'breaking', 'alert', 'dangerous', 'exposed', 'scandal']
    }
    
    analysis = []
    for item in coverage:
        title = item.get('title', '').lower()
        emotion_type = None
        
        for emo_type, words in emotional_words.items():
            if any(w in title for w in words):
                emotion_type = emo_type
                break
        
        analysis.append({
            'title': item.get('title', ''),
            'community': item.get('community', '?'),
            'score': item.get('score', 0),
            'emotion_type': emotion_type
        })
    
    return analysis

def main():
    print("=" * 60)
    print("🔍 PERSPECTIVE AGGREGATOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    topic = "AI"
    print("\n📌 Default search: 'AI'")
    
    coverage = fetch_topic_coverage(topic)
    analysis = analyze_perspectives(coverage)
    
    print("\n" + "=" * 60)
    print("📊 COMMUNITY COVERAGE")
    print("=" * 60)
    
    community_counts = Counter(item['community'] for item in analysis)
    for community, count in community_counts.most_common():
        bar = "█" * count
        print(f"   {community:15} {bar} {count}")
    
    print("\n" + "=" * 60)
    print("😈 SPIN DETECTION")
    print("=" * 60)
    
    emotional = [a for a in analysis if a.get('emotion_type')]
    if emotional:
        print(f"\n   Found {len(emotional)} emotionally charged titles")
    else:
        print("\n   ✅ No obvious emotional spin detected")
    
    print("\n" + "=" * 60)
    print("💡 KEY INSIGHT")
    print("=" * 60)
    
    print("""
   Each community frames topics differently:
   • r/technology: Focuses on innovation
   • r/politics: Focuses on policy controversy
   • r/worldnews: Focuses on conflict
   • r/science: Focuses on research
   • r/news: General coverage
   
   Same event, different perspective.
    """)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'topic': topic,
        'total_coverage': len(coverage),
        'communities': list(community_counts.keys()),
        'analysis': analysis[:20]
    }
    
    with open('/output/perspective_aggregator.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n✅ Saved to /output/perspective_aggregator.json")

if __name__ == "__main__":
    main()