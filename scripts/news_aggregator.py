#!/usr/bin/env python3
"""
World News Aggregator - Fetches from multiple news sources
Combines: Reddit, HackerNews, and news API headlines
"""

import json
import urllib.request
from datetime import datetime

def fetch_news_org():
    """Fetch from NewsAPI (free tier) - headlines only"""
    try:
        # NewsAPI requires API key, so we'll use a different approach
        # Using GNews API (free tier available)
        url = "https://gnews.io/api/v4/top-headlines?category=world&lang=en&max=10&apikey=demo"
        req = urllib.request.Request(url, headers={'User-Agent': 'NewsAggregator/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            articles = []
            for article in data.get('articles', [])[:10]:
                articles.append({
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'title': article.get('title', ''),
                    'description': article.get('description', '')[:200],
                    'url': article.get('url', ''),
                    'published': article.get('publishedAt', '')[:10]
                })
            return articles
    except Exception as e:
        return [{'error': str(e), 'source': 'NewsAPI'}]

def fetch_bing_news():
    """Fetch trending news via Bing (unofficial)"""
    try:
        # Using Bing's RSS feeds (public)
        url = "https://www.bing.com/rss/news?q=world&setlang=en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            import xml.etree.ElementTree as ET
            content = resp.read().decode('utf-8')
            root = ET.fromstring(content)
            
            items = []
            for item in root.findall('.//item')[:10]:
                title = item.find('title')
                desc = item.find('description')
                link = item.find('link')
                
                items.append({
                    'source': 'Bing News',
                    'title': title.text if title is not None else '',
                    'description': (desc.text[:200] if desc is not None else '').replace('<![CDATA[', '').replace(']]>', ''),
                    'url': link.text if link is not None else ''
                })
            return items
    except Exception as e:
        return [{'error': str(e), 'source': 'Bing RSS'}]

def fetch_reddit_news():
    """Get news from Reddit"""
    subreddits = ['news', 'worldnews', 'politics']
    all_news = []
    
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            req = urllib.request.Request(url, headers={'User-Agent': 'NewsAggregator/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                for child in data.get('data', {}).get('children', [])[:3]:
                    post = child.get('data', {})
                    all_news.append({
                        'source': f'r/{sub}',
                        'title': post.get('title', ''),
                        'score': post.get('score', 0),
                        'url': f"https://reddit.com{post.get('permalink', '')}"
                    })
        except Exception as e:
            pass
    
    return all_news

def aggregate_news():
    print("=" * 60)
    print("📰 WORLD NEWS AGGREGATOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    all_news = []
    
    # Fetch from Reddit
    print("\n📦 Fetching from Reddit...")
    reddit_news = fetch_reddit_news()
    print(f"   ✅ Got {len(reddit_news)} posts")
    for news in reddit_news[:5]:
        print(f"   [{news['source']}] {news['title'][:60]}... ({news['score']} pts)")
    all_news.extend(reddit_news)
    
    # Try Bing RSS
    print("\n📦 Fetching from Bing RSS...")
    bing_news = fetch_bing_news()
    if bing_news and 'error' not in bing_news[0]:
        print(f"   ✅ Got {len(bing_news)} articles")
        for news in bing_news[:5]:
            print(f"   [Bing] {news['title'][:60]}...")
        all_news.extend(bing_news)
    else:
        print(f"   ⚠️  {bing_news[0].get('error', 'Failed')}")
    
    # Categorize by source type
    sources = {}
    for news in all_news:
        src = news.get('source', 'unknown')
        if src not in sources:
            sources[src] = []
        sources[src].append(news)
    
    print("\n" + "=" * 60)
    print("📊 NEWS BY SOURCE")
    print("=" * 60)
    for src, items in sources.items():
        print(f"\n   {src}: {len(items)} articles")
        for item in items[:2]:
            print(f"      • {item.get('title', '')[:55]}...")
    
    # Sort by score (for reddit) or just list order
    def get_score(news):
        return news.get('score', 0)
    
    top_news = sorted(all_news, key=get_score, reverse=True)[:10]
    
    print("\n" + "=" * 60)
    print("🔥 TOP 10 NEWS (by engagement)")
    print("=" * 60)
    for i, news in enumerate(top_news, 1):
        title = news.get('title', '')[:65]
        score = news.get('score', 0)
        src = news.get('source', '?')
        print(f"   {i}. [{src}] {title}...")
        if score > 0:
            print(f"      ↑ {score} engagement")
    
    # Save
    result = {
        'timestamp': datetime.now().isoformat(),
        'total_articles': len(all_news),
        'sources': list(sources.keys()),
        'top_news': top_news,
        'all_news': all_news
    }
    
    with open('/output/world_news_aggregator.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n✅ Saved to /output/world_news_aggregator.json")
    
    return result

if __name__ == "__main__":
    aggregate_news()