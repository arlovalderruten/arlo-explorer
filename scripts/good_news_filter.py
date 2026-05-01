#!/usr/bin/env python3
"""
Good News Filter - Finds positive developments that under-reported
Searches for: scientific breakthroughs, collaborative efforts, improvements
"""

import json
import urllib.request
from datetime import datetime
from collections import Counter

# Keywords for positive news
POSITIVE_KEYWORDS = {
    'scientific': ['breakthrough', 'discovery', 'research', 'study', 'found', 'new cure', 'vaccine', 'treatment', 'success', 'advance'],
    'collaborative': ['partnership', 'agreement', 'treaty', 'collaboration', 'united', 'cooperation', 'peace', 'accord'],
    'improvement': ['declined', 'reduced', 'improved', 'increase', 'growth', 'decline', 'eliminated', 'eradicated', 'resolved'],
    'progress': ['launch', 'complete', 'finished', 'inaugurated', 'opened', 'built', 'achieved', 'milestone'],
    'humanitarian': ['aid', 'relief', 'support', 'rescue', 'saved', 'helped', 'donated', 'volunteer']
}

def search_nasa_good_news():
    """Get recent positive NASA discoveries"""
    try:
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        req = urllib.request.Request(url, headers={'User-Agent': 'GoodNewsBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                'source': 'NASA',
                'title': data.get('title', ''),
                'description': data.get('explanation', '')[:300],
                'category': 'scientific',
                'positive_indicator': 'space exploration'
            }
    except:
        return None

def get_reddit_good_news():
    """Get positive posts from Reddit"""
    try:
        url = "https://www.reddit.com/r/UpliftingNews/hot.json?limit=20"
        req = urllib.request.Request(url, headers={'User-Agent': 'GoodNewsBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            posts = []
            for child in data.get('data', {}).get('children', [])[:10]:
                post = child.get('data', {})
                posts.append({
                    'title': post.get('title', ''),
                    'score': post.get('score', 0),
                    'source': 'r/UpliftingNews'
                })
            return posts
    except:
        return []

def get_world_improvements():
    """Get news about world improvements"""
    try:
        url = "https://www.reddit.com/r/WorldNews/hot.json?limit=20"
        req = urllib.request.Request(url, headers={'User-Agent': 'GoodNewsBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            good_news = []
            for child in data.get('data', {}).get('children', [])[:20]:
                post = child.get('data', {})
                title = post.get('title', '').lower()
                
                # Check for positive indicators
                for category, keywords in POSITIVE_KEYWORDS.items():
                    if any(k in title for k in keywords):
                        good_news.append({
                            'title': post.get('title', ''),
                            'score': post.get('score', 0),
                            'category': category,
                            'source': 'r/worldnews'
                        })
                        break
            return good_news
    except:
        return []

def get_science_breakthroughs():
    """Get science news"""
    try:
        url = "https://www.reddit.com/r/science/hot.json?limit=20"
        req = urllib.request.Request(url, headers={'User-Agent': 'GoodNewsBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            breakthroughs = []
            for child in data.get('data', {}).get('children', [])[:15]:
                post = child.get('data', {})
                title = post.get('title', '').lower()
                
                for keyword in POSITIVE_KEYWORDS['scientific']:
                    if keyword in title:
                        breakthroughs.append({
                            'title': post.get('title', ''),
                            'score': post.get('score', 0),
                            'category': 'scientific',
                            'source': 'r/science'
                        })
                        break
            return breakthroughs
    except Exception as e:
        return []

def analyze_positive_coverage():
    """Analyze overall positive coverage"""
    reddit_good = get_reddit_good_news()
    world_improvements = get_world_improvements()
    science = get_science_breakthroughs()
    nasa = search_nasa_good_news()
    
    print("=" * 60)
    print("✅ GOOD NEWS FILTER")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    print("\n📥 Fetching positive news...")
    print(f"   ✅ UpliftingNews: {len(reddit_good)} posts")
    print(f"   ✅ WorldNews positive: {len(world_improvements)} items")
    print(f"   ✅ Science breakthroughs: {len(science)} items")
    print(f"   ✅ NASA: {'found' if nasa else 'not found'}")
    
    # Display good news from Reddit
    print("\n" + "=" * 60)
    print("🌟 TOP POSITIVE STORIES")
    print("=" * 60)
    
    all_good = reddit_good + world_improvements + science
    all_good.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    for i, story in enumerate(all_good[:10], 1):
        title = story.get('title', '')[:65]
        score = story.get('score', 0)
        source = story.get('source', '?')
        cat = story.get('category', 'general')
        
        cat_icon = {
            'scientific': '🔬',
            'collaborative': '🤝',
            'improvement': '📈',
            'progress': '🚀',
            'humanitarian': '❤️'
        }.get(cat, '📌')
        
        print(f"\n{i}. {cat_icon} [{source}]")
        print(f"   {title}...")
        print(f"   📈 {score} pts")
    
    # Category breakdown
    print("\n" + "=" * 60)
    print("📊 POSITIVE COVERAGE BREAKDOWN")
    print("=" * 60)
    
    categories = [s.get('category', 'other') for s in all_good]
    cat_counts = Counter(categories)
    
    for cat, count in cat_counts.most_common():
        cat_icon = {
            'scientific': '🔬',
            'collaborative': '🤝',
            'improvement': '📈',
            'progress': '🚀',
            'humanitarian': '❤️',
            'other': '📌'
        }.get(cat, '📌')
        
        print(f"   {cat_icon} {cat}: {count} stories")
    
    # World improvements tracker
    print("\n" + "=" * 60)
    print("🌍 WHAT'S ACTUALLY IMPROVING")
    print("=" * 60)
    
    improvements = [
        "🌱 Global poverty has halved in 20 years",
        "📚 Literacy rates at all-time highs globally",
        "💊 Life expectancy increased 6 years since 1990",
        "🦠 Smallpox eradicated, polio near elimination",
        "☀️ Solar power cheapest in history",
        "🌊 Clean water access for billions more people",
        "📉 Child mortality cut in half since 1990"
    ]
    
    for imp in improvements:
        print(f"   ✅ {imp}")
    
    # NASA highlight
    if nasa:
        print("\n" + "=" * 60)
        print("🔭 SCIENTIFIC DISCOVERY OF THE DAY")
        print("=" * 60)
        print(f"\n   📌 {nasa['title']}")
        print(f"   {nasa['description'][:200]}...")
    
    # Generate perspective
    print("\n" + "=" * 60)
    print("💡 PERSPECTIVE")
    print("=" * 60)
    
    total_reddit = len(get_reddit_good_news()) if not all_good else 0
    total_world = len(world_improvements)
    total_science = len(science)
    
    if total_science > 0 or total_world > 0:
        print("\n   While conflict dominates headlines, there's actually")
        print("   a lot of positive progress happening:")
        print(f"   • {total_science} scientific breakthroughs shared today")
        print(f"   • {total_world} positive world developments")
        print("   • Uplifting news exists but gets less attention")
        print("\n   The world is improving on many metrics, but good")
        print("   news doesn't generate clicks like conflict does.")
    
    # Save results
    result = {
        'timestamp': datetime.now().isoformat(),
        'positive_count': len(all_good),
        'categories': dict(cat_counts),
        'top_stories': all_good[:10],
        'world_improvements': improvements,
        'nasa_highlight': nasa
    }
    
    with open('/output/good_news_filter.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # Generate markdown
    md = f"""# ✅ Good News Filter

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

## Positive Stories Found: {len(all_good)}

"""
    
    for i, story in enumerate(all_good[:10], 1):
        md += f"{i}. **{story.get('title', '')}**\n"
        md += f"   - Source: {story.get('source', '?')} | Score: {story.get('score', '?')}\n\n"
    
    md += """
## World Improvements

"""
    for imp in improvements:
        md += f"- {imp}\n"
    
    md += f"""

## Scientific Discovery

**{nasa.get('title', 'N/A') if nasa else 'N/A'}**

{nasa.get('description', '')[:300] if nasa else ''}...

---

*Good news exists but often gets buried by conflict coverage*
"""
    
    with open('/output/good_news_filter.md', 'w') as f:
        f.write(md)
    
    print("\n" + "=" * 60)
    print("✅ Saved to good_news_filter.json and .md")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    analyze_positive_coverage()