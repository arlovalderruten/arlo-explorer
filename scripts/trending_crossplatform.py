#!/usr/bin/env python3
"""
Trending Cross-Platform - What's hot across HN, Reddit, and GitHub
Creates a unified view of trending topics
"""

import json
import urllib.request
from datetime import datetime
from collections import Counter

def fetch_hn_top():
    """Get top HN stories with scores"""
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'TrendingBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            top_ids = json.loads(resp.read())[:20]
        
        stories = []
        for story_id in top_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url, headers={'User-Agent': 'TrendingBot/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                story = json.loads(resp.read())
                if story.get('title'):
                    stories.append({
                        'platform': 'HackerNews',
                        'title': story['title'],
                        'score': story.get('score', 0),
                        'url': story.get('url', '')
                    })
        return stories
    except:
        return []

def fetch_reddit_multi():
    """Get hot posts from multiple subs"""
    subs = ['news', 'worldnews', 'technology', 'programming', 'science']
    all_posts = []
    
    for sub in subs:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            req = urllib.request.Request(url, headers={'User-Agent': 'TrendingBot/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                for child in data.get('data', {}).get('children', [])[:3]:
                    post = child.get('data', {})
                    all_posts.append({
                        'platform': f'r/{sub}',
                        'title': post.get('title', ''),
                        'score': post.get('score', 0)
                    })
        except:
            pass
    
    return all_posts

def extract_topics(items):
    """Extract main topics from titles"""
    keywords = {
        'AI/ML': ['ai', 'machine learning', 'llm', 'gpt', 'neural', 'model', 'openai', 'claude', 'gemini'],
        'Security': ['security', 'hack', 'vulnerability', 'breach', 'cyber', 'malware', 'attack'],
        'Web Dev': ['javascript', 'python', 'react', 'rust', 'web', 'frontend', 'api', 'docker'],
        'Politics': ['trump', 'biden', 'government', 'congress', 'election', 'war', 'ukraine', 'iran'],
        'Business': ['startup', 'funding', 'acquisition', 'ipo', 'stock', 'market', 'company'],
        'Science': ['space', 'nasa', 'research', 'study', 'science', 'discover'],
        'Gaming': ['game', 'steam', 'playstation', 'xbox', 'nintendo'],
        'Crypto': ['bitcoin', 'crypto', 'ethereum', 'blockchain', 'nft']
    }
    
    topics = []
    for item in items:
        title = item.get('title', '').lower()
        for topic, keywords_list in keywords.items():
            if any(k in title for k in keywords_list):
                topics.append(topic)
                break
    
    return topics

def main():
    print("=" * 60)
    print("📊 TRENDING CROSS-PLATFORM")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Fetch all
    print("\n📥 Fetching from platforms...")
    hn_stories = fetch_hn_top()
    reddit_posts = fetch_reddit_multi()
    
    print(f"   ✅ HN: {len(hn_stories)} stories")
    print(f"   ✅ Reddit: {len(reddit_posts)} posts")
    
    # Combine and rank by score
    all_items = hn_stories + reddit_posts
    all_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Top items by platform
    print("\n" + "=" * 60)
    print("🏆 TOP 10 TRENDING (by engagement)")
    print("=" * 60)
    
    for i, item in enumerate(all_items[:10], 1):
        title = item.get('title', '')[:60]
        score = item.get('score', 0)
        platform = item.get('platform', '?')
        print(f"\n   {i}. [{platform}]")
        print(f"      {title}...")
        print(f"      📈 {score} engagement")
    
    # Topic analysis
    print("\n" + "=" * 60)
    print("📈 TOPIC DISTRIBUTION")
    print("=" * 60)
    
    topics = extract_topics(all_items)
    topic_counts = Counter(topics)
    
    total = len(topics) or 1
    for topic, count in topic_counts.most_common():
        pct = count / total * 100
        bar = "█" * int(pct / 5)
        print(f"   {topic:12} {bar:20} {pct:5.1f}% ({count})")
    
    if not topic_counts:
        print("   (no clear topic pattern)")
    
    # Platform breakdown
    print("\n" + "=" * 60)
    print("📱 PLATFORM BREAKDOWN")
    print("=" * 60)
    
    platforms = Counter(item.get('platform', '?') for item in all_items)
    total_platform = len(all_items) or 1
    
    for platform, count in platforms.most_common():
        pct = count / total_platform * 100
        bar = "█" * int(pct / 5)
        print(f"   {platform:15} {bar:20} {pct:5.1f}% ({count})")
    
    # Generate insights
    top_topic = topic_counts.most_common(1)[0] if topic_counts else None
    
    print("\n" + "=" * 60)
    print("💡 INSIGHTS")
    print("=" * 60)
    
    if top_topic:
        print(f"\n   🔥 Hot topic: {top_topic[0]} ({top_topic[1]} mentions)")
    
    # What HN is talking about vs Reddit
    hn_topics = extract_topics(hn_stories[:10])
    reddit_topics = extract_topics(reddit_posts[:10])
    
    hn_counter = Counter(hn_topics)
    reddit_counter = Counter(reddit_topics)
    
    print(f"\n   📰 HackerNews top: {hn_counter.most_common(1)[0][0] if hn_counter else 'N/A'}")
    print(f"   📱 Reddit top: {reddit_counter.most_common(1)[0][0] if reddit_counter else 'N/A'}")
    
    if hn_counter.most_common(1)[0][0] == reddit_counter.most_common(1)[0][0]:
        print("   ✅ Both platforms aligned on same topic!")
    else:
        print("   ⚠️  Platform interests diverge")
    
    # Save results
    result = {
        'timestamp': datetime.now().isoformat(),
        'total_items': len(all_items),
        'hn_count': len(hn_stories),
        'reddit_count': len(reddit_posts),
        'topics': dict(topic_counts),
        'platforms': dict(platforms),
        'top_10': all_items[:10]
    }
    
    with open('/output/trending_crossplatform.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Saved to /output/trending_crossplatform.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()