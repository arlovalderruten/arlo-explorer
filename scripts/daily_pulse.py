#!/usr/bin/env python3
"""
Daily Pulse - A synthesized daily briefing from public APIs
Combines: GitHub trending, HackerNews, Reddit, NASA APOD
"""

import json
import urllib.request
from datetime import datetime

def fetch_nasa_apod():
    """Fetch NASA's Astronomy Picture of the Day"""
    try:
        # NASA APOD API (demo key - works for basic requests)
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyPulse/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                'source': 'NASA APOD',
                'title': data.get('title', 'Unknown'),
                'date': data.get('date', ''),
                'explanation': data.get('explanation', '')[:200],
                'media_type': data.get('media_type', 'unknown'),
                'url': data.get('url', '')
            }
    except Exception as e:
        return {'source': 'NASA APOD', 'error': str(e)}

def fetch_wikipedia_news():
    """Fetch current events from Wikipedia"""
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/Current_events"
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyPulse/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                'source': 'Wikipedia Current Events',
                'title': data.get('title', 'Current Events'),
                'extract': data.get('extract', '')[:300],
                'timestamp': data.get('timestamp', '')
            }
    except Exception as e:
        return {'source': 'Wikipedia', 'error': str(e)}

def generate_pulse():
    """Generate the daily pulse"""
    print("=" * 60)
    print("📡 DAILY PULSE - Public Data Synthesis")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    pulse_data = {
        'generated_at': datetime.now().isoformat(),
        'sections': []
    }
    
    # NASA
    print("\n🔭 NASA Astronomy Picture of the Day...")
    nasa = fetch_nasa_apod()
    if 'error' in nasa:
        print(f"   ❌ {nasa['error']}")
    else:
        print(f"   ✅ {nasa['title']}")
        pulse_data['sections'].append({
            'category': 'Science & Space',
            'title': nasa['title'],
            'date': nasa['date'],
            'content': nasa['explanation'],
            'source': 'NASA APOD'
        })
    
    # Wikipedia Current Events
    print("\n📰 Wikipedia Current Events...")
    wiki = fetch_wikipedia_news()
    if 'error' in wiki:
        print(f"   ❌ {wiki['error']}")
    else:
        print(f"   ✅ {wiki['title']}")
        pulse_data['sections'].append({
            'category': 'World Events',
            'title': wiki['title'],
            'content': wiki['extract'],
            'source': 'Wikipedia'
        })
    
    # Load previous data
    print("\n🔗 Syncing with CDS results...")
    try:
        with open('/output/cds_real_results.json') as f:
            cds = json.load(f)
            # Add tech and geopolitics insights from earlier
            if 'insights' in cds:
                for insight in cds.get('insights', [])[:2]:
                    pulse_data['sections'].append({
                        'category': 'Synthesized Insight',
                        'title': 'CDS Bridge Concept',
                        'content': insight.strip()[:300],
                        'source': 'Cross-Disciplinary Synthesis'
                    })
    except:
        print("   ⚠️  No previous CDS data found")
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📋 DAILY BRIEFING SUMMARY")
    print("=" * 60)
    
    for i, section in enumerate(pulse_data['sections'], 1):
        print(f"\n{i}. [{section['category']}]")
        print(f"   {section['title']}")
        content = section.get('content', '')[:100]
        if content:
            print(f"   {content}...")
    
    # Save pulse
    pulse_data['section_count'] = len(pulse_data['sections'])
    
    with open('/output/daily_pulse.json', 'w') as f:
        json.dump(pulse_data, f, indent=2)
    
    # Generate markdown version
    md = f"""# 📡 Daily Pulse - {datetime.now().strftime('%Y-%m-%d')}

## Generated: {pulse_data['generated_at']}

"""
    for section in pulse_data['sections']:
        md += f"""### [{section['category']}] {section['title']}

{section.get('content', section.get('explanation', ''))[:400]}

_Source: {section['source']}_

---

"""
    
    with open('/output/daily_pulse.md', 'w') as f:
        f.write(md)
    
    print("\n" + "=" * 60)
    print("✅ Daily Pulse generated!")
    print("   📄 /output/daily_pulse.json")
    print("   📄 /output/daily_pulse.md")
    print("=" * 60)
    
    return pulse_data

if __name__ == "__main__":
    generate_pulse()