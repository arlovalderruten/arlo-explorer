#!/usr/bin/env python3
"""
Universal Data Collector - Fetches from multiple APIs
Adds: Weather, Crypto prices, News headlines
"""

import json
import urllib.request
from datetime import datetime

def fetch_weather():
    """Get current weather for NYC (default)"""
    try:
        # wttr.in is a free weather API
        url = "https://wttr.in/NewYork?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            current = data.get('current_condition', [{}])[0]
            return {
                'source': 'wttr.in',
                'location': 'New York',
                'temp_C': current.get('temp_C', 'N/A'),
                'temp_F': current.get('temp_F', 'N/A'),
                'condition': current.get('weatherDesc', [{}])[0].get('value', 'Unknown'),
                'humidity': current.get('humidity', 'N/A'),
                'wind': current.get('windspeedKmph', 'N/A')
            }
    except Exception as e:
        return {'source': 'wttr.in', 'error': str(e)}

def fetch_crypto_top():
    """Get top crypto prices via CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1&sparkline=false"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            coins = []
            for coin in data:
                coins.append({
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name', ''),
                    'price_usd': coin.get('current_price', 0),
                    'change_24h': coin.get('price_change_percentage_24h', 0),
                    'market_cap': coin.get('market_cap', 0)
                })
            return coins
    except Exception as e:
        return [{'error': str(e)}]

def fetch_github_events():
    """Get recent events from a popular repo"""
    try:
        # Get events from a popular repo
        url = "https://api.github.com/repos/microsoft/vscode/events?per_page=5"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            events = []
            for event in data[:5]:
                events.append({
                    'type': event.get('type', 'Unknown'),
                    'actor': event.get('actor', {}).get('login', 'Unknown'),
                    'repo': event.get('repo', {}).get('name', ''),
                    'created': event.get('created_at', '')[:10]
                })
            return events
    except Exception as e:
        return [{'error': str(e)}]

def collect_all():
    """Collect from all sources"""
    print("=" * 60)
    print("🌐 UNIVERSAL DATA COLLECTOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    data = {'timestamp': datetime.now().isoformat(), 'sources': {}}
    
    print("\n🌤️  Fetching weather...")
    weather = fetch_weather()
    if 'error' in weather:
        print(f"   ❌ {weather['error']}")
    else:
        print(f"   ✅ {weather['condition']}, {weather['temp_F']}°F")
        data['sources']['weather'] = weather
    
    print("\n💰 Fetching crypto prices...")
    crypto = fetch_crypto_top()
    if 'error' in crypto:
        print(f"   ❌ {crypto[0]['error']}")
    else:
        print(f"   ✅ {len(crypto)} coins")
        for c in crypto[:3]:
            arrow = "📈" if c['change_24h'] > 0 else "📉"
            print(f"   {arrow} {c['symbol']}: ${c['price_usd']:,.2f} ({c['change_24h']:.1f}%)")
        data['sources']['crypto'] = crypto
    
    print("\n🔔 Fetching GitHub activity...")
    events = fetch_github_events()
    if 'error' in events:
        print(f"   ❌ {events[0]['error']}")
    else:
        print(f"   ✅ {len(events)} recent events")
        for e in events[:3]:
            print(f"   • {e['type']} by {e['actor']}")
        data['sources']['github_events'] = events
    
    # Save
    with open('/output/universal_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\n✅ Saved to /output/universal_data.json")
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📋 QUICK SUMMARY")
    print("=" * 60)
    
    if 'weather' in data['sources']:
        w = data['sources']['weather']
        print(f"\nWeather: {w['condition']}, {w['temp_F']}°F in {w['location']}")
    
    if 'crypto' in data['sources']:
        print(f"\nCrypto Market:")
        for c in data['sources']['crypto'][:5]:
            change = c['change_24h']
            arrow = "🟢" if change > 0 else "🔴"
            print(f"  {arrow} {c['symbol']}: ${c['price_usd']:,.0f} ({change:+.1f}%)")
    
    return data

if __name__ == "__main__":
    collect_all()