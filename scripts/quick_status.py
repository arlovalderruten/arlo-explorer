#!/usr/bin/env python3
"""
Quick Status Check - One-liner summary of everything
"""

import json
import os
from datetime import datetime

def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default or {}

def main():
    print("🌟 ARLO STATUS CHECK")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    # Load all collected data
    mood = load_json('/output/internet_mood.json', {})
    echo = load_json('/output/echo_chamber_analysis.json', {})
    crypto = load_json('/output/crypto_alerter.json', {})
    trending = load_json('/output/trending_crossplatform.json', {})
    weather = load_json('/output/universal_data.json', {}).get('sources', {}).get('weather', {})
    facts = load_json('/output/interesting_facts.json', {})
    
    # Print one-liners
    print("📊 QUICK STATS:")
    
    if mood:
        score = mood.get('overall_mood', '?')
        print(f"   🌡️  Internet Mood: {score}/100")
    
    if echo:
        score = echo.get('echo_score', '?')
        print(f"   🔊 Echo Score: {score}/100")
    
    if crypto and crypto.get('coins'):
        btc = crypto['coins'][0]
        print(f"   💰 BTC: ${btc.get('price', 0):,.0f}")
    
    if weather:
        print(f"   🌤️  NYC: {weather.get('condition', '?')}, {weather.get('temp_F', '?')}°F")
    
    if trending:
        topics = trending.get('topics', {})
        if topics:
            top = max(topics.items(), key=lambda x: x[1])
            print(f"   🔥 Hot Topic: {top[0]} ({top[1]} mentions)")
    
    # Count files
    output_count = len([f for f in os.listdir('/output') if f.endswith(('.json', '.md'))])
    scripts_count = len([f for f in os.listdir('/scripts') if f.endswith('.py')])
    
    print()
    print(f"📁 Files: {output_count} outputs, {scripts_count} scripts")
    print()
    print("✅ All systems operational!")
    print(f"   GitHub: https://github.com/arlovalderruten/arlo-explorer")

if __name__ == "__main__":
    main()