#!/usr/bin/env python3
"""
World State Dashboard - Combines all data sources into one view
Generates a comprehensive "state of the world" report
"""

import json
from datetime import datetime
from pathlib import Path

def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default or {}

def generate_dashboard():
    print("=" * 60)
    print("🌍 WORLD STATE DASHBOARD")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Load all collected data
    mood = load_json('/output/internet_mood.json', {})
    weather = load_json('/output/universal_data.json', {}).get('sources', {}).get('weather', {})
    crypto = load_json('/output/universal_data.json', {}).get('sources', {}).get('crypto', [])
    cds = load_json('/output/cds_real_results.json', {})
    pulse = load_json('/output/daily_pulse.json', {})
    
    dashboard = {
        'generated_at': datetime.now().isoformat(),
        'sections': {}
    }
    
    # Internet Mood Section
    print("\n" + "━" * 40)
    print("🌡️  INTERNET SENTIMENT")
    print("━" * 40)
    
    if mood:
        mood_score = mood.get('overall_mood', 50)
        mood_label = mood.get('overall_label', 'neutral')
        hn_mood = mood.get('hn_mood', 50)
        reddit_mood = mood.get('reddit_mood', 50)
        
        if mood_score > 60:
            emoji = "😄"
        elif mood_score > 45:
            emoji = "😐"
        else:
            emoji = "😰"
        
        print(f"   Overall: {emoji} {mood_score}/100 ({mood_label})")
        print(f"   HackerNews: {hn_mood}/100")
        print(f"   Reddit: {reddit_mood}/100")
        
        dashboard['sections']['internet_mood'] = {
            'score': mood_score,
            'label': mood_label,
            'hn_score': hn_mood,
            'reddit_score': reddit_mood
        }
    
    # World Events Section
    print("\n" + "━" * 40)
    print("📰 TOP WORLD EVENTS")
    print("━" * 40)
    
    if mood and 'top_stories' in mood:
        for i, story in enumerate(mood.get('top_stories', [])[:5], 1):
            title = story.get('title', '')[:65]
            print(f"   {i}. [{story.get('source', '?')}] {title}...")
        dashboard['sections']['top_stories'] = mood.get('top_stories', [])[:5]
    
    # Crypto Section
    print("\n" + "━" * 40)
    print("💰 CRYPTO MARKETS")
    print("━" * 40)
    
    if crypto:
        for coin in crypto[:5]:
            price = coin.get('price_usd', 0)
            change = coin.get('change_24h', 0)
            arrow = "🟢" if change > 0 else "🔴"
            symbol = coin.get('symbol', '?')
            name = coin.get('name', '')[:20]
            print(f"   {arrow} {symbol:5} ${price:>12,.2f}  ({change:+.1f}%)")
        dashboard['sections']['crypto'] = crypto[:5]
    
    # Weather Section
    print("\n" + "━" * 40)
    print("🌤️  WEATHER")
    print("━" * 40)
    
    if weather:
        loc = weather.get('location', 'Unknown')
        condition = weather.get('condition', 'Unknown')
        temp_f = weather.get('temp_F', '?')
        humidity = weather.get('humidity', '?')
        print(f"   {loc}: {condition}, {temp_f}°F")
        print(f"   Humidity: {humidity}%")
        dashboard['sections']['weather'] = weather
    
    # Science/Space Section (from NASA)
    print("\n" + "━" * 40)
    print("🔭 SCIENCE HIGHLIGHT")
    print("━" * 40)
    
    if pulse and pulse.get('sections'):
        for section in pulse.get('sections', []):
            if section.get('category') == 'Science & Space':
                title = section.get('title', 'N/A')
                print(f"   {title}")
                content = section.get('content', '')[:150]
                if content:
                    print(f"   {content}...")
    
    # CDS Insights Section
    print("\n" + "━" * 40)
    print("🧠 SYNTHESIZED INSIGHTS")
    print("━" * 40)
    
    if cds and cds.get('insights'):
        for i, insight in enumerate(cds.get('insights', [])[:2], 1):
            # Extract key phrase
            lines = insight.strip().split('\n')
            for line in lines:
                if 'BRIDGE CONCEPT:' in line:
                    print(f"   {i}. {line.replace('BRIDGE CONCEPT:', '🔗 ').strip()}")
                    break
        dashboard['sections']['insights'] = cds.get('insights', [])[:3]
    
    # Generate emoji summary
    print("\n" + "=" * 60)
    print("📊 WORLD STATE SUMMARY")
    print("=" * 60)
    
    if mood:
        mood_score = mood.get('overall_mood', 50)
        if mood_score < 40:
            print("   🌍 The world feels heavy today")
        elif mood_score < 55:
            print("   🌍 Mixed signals from the world")
        else:
            print("   🌍 Optimism persists despite challenges")
    
    if crypto:
        btc = next((c for c in crypto if c.get('symbol') == 'BTC'), None)
        if btc:
            print(f"   💰 BTC at ${btc.get('price_usd', 0):,.0f}")
    
    if weather:
        print(f"   🌤️  {weather.get('condition', 'Unknown')}, {weather.get('temp_F', '?')}°F")
    
    print(f"\n   ⏰ Report generated: {datetime.now().strftime('%H:%M UTC')}")
    
    # Save dashboard
    dashboard['version'] = '1.0'
    
    with open('/output/world_state_dashboard.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    # Generate markdown
    md = f"""# 🌍 World State Dashboard

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

---

## 🌡️ Internet Sentiment

"""
    if mood:
        md += f"- **Mood Score**: {mood.get('overall_mood', 50)}/100 ({mood.get('overall_label', 'neutral')})\n"
        md += f"- **HackerNews**: {mood.get('hn_mood', 50)}/100\n"
        md += f"- **Reddit**: {mood.get('reddit_mood', 50)}/100\n"
    
    md += """
---

## 📰 Top World Events

"""
    if mood and 'top_stories' in mood:
        for story in mood.get('top_stories', [])[:5]:
            md += f"- **{story.get('source', '?')}** ({story.get('score', 0)} pts)\n  {story.get('title', '')[:80]}...\n\n"
    
    md += """
---

## 💰 Crypto Markets

| Coin | Price | 24h Change |
|------|-------|------------|
"""
    if crypto:
        for coin in crypto[:5]:
            change = coin.get('change_24h', 0)
            arrow = "🟢" if change > 0 else "🔴"
            md += f"| {coin.get('symbol', '?')} | ${coin.get('price_usd', 0):,.2f} | {arrow} {change:+.1f}% |\n"
    
    md += """
---

*Dashboard generated by Arlo's Universal Data Collector*
"""
    
    with open('/output/world_state_dashboard.md', 'w') as f:
        f.write(md)
    
    print("\n✅ Dashboard saved!")
    print("   📄 /output/world_state_dashboard.json")
    print("   📄 /output/world_state_dashboard.md")

if __name__ == "__main__":
    generate_dashboard()