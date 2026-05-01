#!/usr/bin/env python3
"""
Internet Mood Tracker - Analyzes sentiment from public feeds
Combines: HackerNews, Reddit, generates a "mood score"
"""

import json
import urllib.request
from datetime import datetime
from collections import Counter

# Keywords for basic sentiment analysis
POSITIVE_WORDS = {
    'breakthrough', 'success', 'achievement', 'growth', 'improve', 'best',
    'win', 'launch', 'release', 'positive', 'amazing', 'great', 'excellent',
    'happy', 'exciting', 'innovative', 'solving', 'helpful', 'progress'
}
NEGATIVE_WORDS = {
    'crisis', 'failure', 'attack', 'war', 'death', 'disaster', 'crash',
    'problem', 'warning', 'danger', 'threat', 'breaking', 'emergency',
    'killed', 'conflict', 'tension', 'fear', 'concern', 'risk', 'crisis'
}
NEUTRAL_WORDS = {
    'news', 'update', 'report', 'analysis', 'study', 'research',
    'data', 'according', 'says', 'announced', 'published', 'finding'
}

def fetch_hn_top():
    """Get top HN stories"""
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'MoodTracker/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            top_ids = json.loads(resp.read())[:15]
        
        stories = []
        for story_id in top_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url, headers={'User-Agent': 'MoodTracker/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                story = json.loads(resp.read())
                if story.get('title'):
                    stories.append({
                        'title': story['title'],
                        'score': story.get('score', 0),
                        'source': 'HN'
                    })
        return stories
    except Exception as e:
        return []

def fetch_reddit_world():
    """Get Reddit worldnews"""
    try:
        url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
        req = urllib.request.Request(url, headers={'User-Agent': 'MoodTracker/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            posts = []
            for child in data.get('data', {}).get('children', [])[:10]:
                post = child.get('data', {})
                posts.append({
                    'title': post.get('title', ''),
                    'score': post.get('score', 0),
                    'source': 'Reddit'
                })
            return posts
    except Exception as e:
        return []

def analyze_sentiment(text):
    """Simple keyword-based sentiment"""
    text_lower = text.lower()
    words = set(text_lower.split())
    
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)
    neutral_count = len(words & NEUTRAL_WORDS)
    
    if pos_count > neg_count:
        return 'positive', pos_count - neg_count
    elif neg_count > pos_count:
        return 'negative', neg_count - pos_count
    else:
        return 'neutral', neutral_count

def calculate_mood_score(items):
    """Calculate overall mood from items"""
    sentiments = []
    for item in items:
        sentiment, confidence = analyze_sentiment(item['title'])
        weight = min(item['score'] / 100, 10)  # Cap weight at 10
        sentiments.append((sentiment, confidence, weight))
    
    if not sentiments:
        return 50, 'neutral'
    
    # Weighted average
    total_score = 0
    total_weight = 0
    for sent, conf, weight in sentiments:
        if sent == 'positive':
            total_score += (conf + 5) * weight
        elif sent == 'negative':
            total_score -= (conf + 5) * weight
        total_weight += weight
    
    if total_weight == 0:
        return 50, 'neutral'
    
    raw = total_score / total_weight
    # Normalize to 0-100
    normalized = 50 + (raw * 5)
    normalized = max(0, min(100, normalized))
    
    if normalized > 60:
        mood = 'positive'
    elif normalized < 40:
        mood = 'negative'
    else:
        mood = 'neutral'
    
    return round(normalized), mood

def generate_report():
    print("=" * 60)
    print("🌡️  INTERNET MOOD TRACKER")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    print("\n📥 Fetching data...")
    hn_stories = fetch_hn_top()
    reddit_posts = fetch_reddit_world()
    
    all_items = hn_stories + reddit_posts
    print(f"   Collected {len(all_items)} items")
    
    # Analyze
    print("\n🔍 Analyzing sentiment...")
    
    hn_mood, hn_label = calculate_mood_score(hn_stories)
    reddit_mood, reddit_label = calculate_mood_score(reddit_posts)
    overall_mood, overall_label = calculate_mood_score(all_items)
    
    print(f"\n   HN Mood:    {hn_mood}/100 ({hn_label})")
    print(f"   Reddit:     {reddit_mood}/100 ({reddit_label})")
    print(f"   Combined:   {overall_mood}/100 ({overall_label})")
    
    # Breakdown by sentiment
    breakdown = {'positive': [], 'negative': [], 'neutral': []}
    for item in all_items:
        sent, conf = analyze_sentiment(item['title'])
        breakdown[sent].append(item['title'][:60])
    
    print("\n📊 SENTIMENT BREAKDOWN:")
    print(f"   ✅ Positive: {len(breakdown['positive'])} stories")
    for t in breakdown['positive'][:3]:
        print(f"      • {t}...")
    print(f"   ❌ Negative: {len(breakdown['negative'])} stories")
    for t in breakdown['negative'][:3]:
        print(f"      • {t}...")
    
    # Top stories
    print("\n🔥 TOP 5 STORIES (by score):")
    sorted_items = sorted(all_items, key=lambda x: x['score'], reverse=True)[:5]
    for i, item in enumerate(sorted_items, 1):
        print(f"   {i}. [{item['source']}] ({item['score']} pts)")
        print(f"      {item['title'][:70]}...")
    
    # Generate emoji
    if overall_mood > 70:
        emoji = "😄"
    elif overall_mood > 55:
        emoji = "🙂"
    elif overall_mood > 45:
        emoji = "😐"
    elif overall_mood > 30:
        emoji = "😟"
    else:
        emoji = "😰"
    
    print(f"\n{emoji} INTERNET MOOD: {overall_mood}/100 ({overall_label})")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_mood': overall_mood,
        'overall_label': overall_label,
        'hn_mood': hn_mood,
        'reddit_mood': reddit_mood,
        'item_count': len(all_items),
        'breakdown': {k: len(v) for k, v in breakdown.items()},
        'top_stories': sorted_items[:5]
    }
    
    with open('/output/internet_mood.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Report saved to /output/internet_mood.json")
    return report

if __name__ == "__main__":
    generate_report()