#!/usr/bin/env python3
"""
Tech Radar - What's being talked about in tech right now
Creates a visual "radar" of tech topics based on HN activity
"""

import json
import urllib.request
from datetime import datetime
from collections import Counter

def get_hn_top():
    """Get top HN stories with metadata"""
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'TechRadar/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            top_ids = json.loads(resp.read())[:30]
        
        stories = []
        for story_id in top_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url, headers={'User-Agent': 'TechRadar/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                story = json.loads(resp.read())
                if story.get('title'):
                    stories.append({
                        'title': story['title'],
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0),
                        'url': story.get('url', '')
                    })
        return stories
    except:
        return []

def categorize_tech(title):
    """Categorize tech topics"""
    categories = {
        'AI/ML': ['ai', 'llm', 'gpt', 'model', 'openai', 'claude', 'gemini', 'machine learning', 'neural', 'deep learning'],
        'Web Dev': ['javascript', 'react', 'vue', 'angular', 'node', 'css', 'html', 'web', 'frontend', 'backend', 'api', 'http'],
        'Systems': ['rust', 'c++', 'golang', 'go', 'kernel', 'linux', 'unix', 'performance', 'optimization'],
        'Security': ['security', 'hack', 'vulnerability', 'breach', 'cyber', 'encrypt', 'auth'],
        'Cloud': ['aws', 'gcp', 'azure', 'cloud', 'kubernetes', 'docker', 'serverless', 'lambda'],
        'Mobile': ['ios', 'android', 'mobile', 'app', 'swift', 'kotlin', 'flutter'],
        'Data': ['database', 'sql', 'postgres', 'mongodb', 'redis', 'data', 'analytics', 'ml'],
        'Startups': ['startup', 'funding', 'y combinator', 'venture', 'ceo', 'company'],
        'Open Source': ['open source', 'github', 'git', 'linux', 'mozilla', 'apache'],
        'Hardware': ['chip', 'cpu', 'gpu', 'nvidia', 'amd', 'intel', 'hardware', 'server']
    }
    
    title_lower = title.lower()
    found = []
    for cat, keywords in categories.items():
        if any(k in title_lower for k in keywords):
            found.append(cat)
    
    return found if found else ['Other']

def main():
    print("=" * 60)
    print("🎯 TECH RADAR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    print("\n📡 Scanning HackerNews...")
    stories = get_hn_top()
    print(f"   ✅ Analyzed {len(stories)} stories")
    
    # Categorize all stories
    all_categories = []
    for story in stories:
        cats = categorize_tech(story['title'])
        for cat in cats:
            all_categories.append({
                'category': cat,
                'score': story['score'],
                'title': story['title']
            })
    
    # Count by category
    category_counts = Counter(item['category'] for item in all_categories)
    category_scores = {}
    for item in all_categories:
        cat = item['category']
        if cat not in category_scores:
            category_scores[cat] = 0
        category_scores[cat] += item['score']
    
    # Sort by score
    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Visual radar
    print("\n" + "=" * 60)
    print("📡 TECH RADAR (by engagement)")
    print("=" * 60)
    
    max_score = sorted_cats[0][1] if sorted_cats else 1
    
    for cat, score in sorted_cats[:10]:
        count = category_counts[cat]
        pct = score / max_score
        dots = "●" * int(pct * 20)
        print(f"   {cat:15} {dots:20} {score:5} pts ({count})")
    
    # Top stories by category
    print("\n" + "=" * 60)
    print("🔥 TOP STORY PER CATEGORY")
    print("=" * 60)
    
    seen_cats = set()
    for item in all_categories:
        cat = item['category']
        if cat not in seen_cats:
            seen_cats.add(cat)
            title = item['title'][:55]
            print(f"\n   [{cat}]")
            print(f"   {title}... ({item['score']} pts)")
    
    # Generate radar zones (like a real radar)
    print("\n" + "=" * 60)
    print("🛸 RADAR ZONES")
    print("=" * 60)
    
    zones = []
    for cat, score in sorted_cats[:6]:
        if score > max_score * 0.5:
            zones.append(('🔴', cat, 'ADOPT'))  # High engagement
        elif score > max_score * 0.25:
            zones.append(('🟡', cat, 'TRIAL'))
        else:
            zones.append(('⚪', cat, 'ASSESS'))
    
    for indicator, cat, status in zones:
        print(f"   {indicator} {cat:15} - {status}")
    
    # Save
    result = {
        'timestamp': datetime.now().isoformat(),
        'categories': dict(sorted_cats),
        'zones': [{'category': z[1], 'status': z[2]} for z in zones],
        'stories_analyzed': len(stories)
    }
    
    with open('/output/tech_radar.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Saved to /output/tech_radar.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()