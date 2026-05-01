#!/usr/bin/env python3
"""
Crypto Alerter - Monitors crypto prices and alerts on significant changes
Uses CoinGecko API (free, no auth required)
"""

import json
import urllib.request
import time
from datetime import datetime
from pathlib import Path

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_top_crypto(limit=20):
    """Get top cryptocurrencies by market cap"""
    try:
        url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={limit}&page=1&sparkline=false"
        req = urllib.request.Request(url, headers={'User-Agent': 'CryptoAlerter/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return [{
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name', ''),
                'price': coin.get('current_price', 0),
                'change_1h': coin.get('price_change_percentage_1h_in_currency', 0),
                'change_24h': coin.get('price_change_percentage_24h', 0),
                'change_7d': coin.get('price_change_percentage_7d_in_currency', 0),
                'volume': coin.get('total_volume', 0),
                'market_cap': coin.get('market_cap', 0)
            } for coin in data]
    except Exception as e:
        return [{'error': str(e)}]

def format_large_number(num):
    """Format large numbers nicely"""
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.0f}"

def check_alerts(coins, alert_file='/output/crypto_alerts.json'):
    """Check for significant price movements and generate alerts"""
    alerts = []
    
    for coin in coins:
        # Check for significant moves (>5% in 1h or >10% in 24h)
        change_1h = abs(coin.get('change_1h', 0) or 0)
        change_24h = abs(coin.get('change_24h', 0) or 0)
        
        if change_1h > 5:
            direction = "📈" if coin['change_1h'] > 0 else "📉"
            alerts.append({
                'type': 'hourly_spike',
                'coin': coin['symbol'],
                'change': f"+{change_1h:.1f}%" if coin['change_1h'] > 0 else f"{change_1h:.1f}%",
                'price': f"${coin['price']:,.4f}" if coin['price'] < 1 else f"${coin['price']:,.2f}",
                'urgency': 'high' if change_1h > 10 else 'medium'
            })
        
        if change_24h > 10:
            direction = "📈" if coin['change_24h'] > 0 else "📉"
            alerts.append({
                'type': 'daily_spike',
                'coin': coin['symbol'],
                'change': f"+{change_24h:.1f}%" if coin['change_24h'] > 0 else f"{change_24h:.1f}%",
                'price': f"${coin['price']:,.4f}" if coin['price'] < 1 else f"${coin['price']:,.2f}",
                'urgency': 'high' if change_24h > 20 else 'medium'
            })
    
    return alerts

def main():
    print("=" * 60)
    print("💹 CRYPTO ALERTER")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Get top 20 crypto
    print("\n📊 Fetching top 20 cryptocurrencies...")
    coins = get_top_crypto(20)
    
    if 'error' in coins[0] if coins else True:
        print(f"   ❌ Error: {coins[0].get('error', 'Unknown')}")
        return
    
    print(f"   ✅ Got {len(coins)} coins")
    
    # Top movers table
    print("\n" + "=" * 60)
    print("📈 TOP 10 BY MARKET CAP")
    print("=" * 60)
    
    print(f"{'#':<3} {'Symbol':<8} {'Price':<15} {'24h':<10} {'7d':<10} {'Market Cap'}")
    print("-" * 60)
    
    for i, coin in enumerate(coins[:10], 1):
        price = coin['price']
        price_str = f"${price:,.4f}" if price < 1 else f"${price:,.2f}"
        
        change_24h = coin.get('change_24h', 0) or 0
        change_7d = coin.get('change_7d', 0) or 0
        
        arrow_24h = "🟢" if change_24h > 0 else "🔴"
        arrow_7d = "🟢" if change_7d > 0 else "🔴"
        
        change_24h_str = f"{arrow_24h}{change_24h:+.1f}%"
        change_7d_str = f"{arrow_7d}{change_7d:+.1f}%"
        
        market_cap = format_large_number(coin.get('market_cap', 0))
        
        print(f"{i:<3} {coin['symbol']:<8} {price_str:<15} {change_24h_str:<10} {change_7d_str:<10} {market_cap}")
    
    # Check for alerts
    print("\n" + "=" * 60)
    print("🚨 ALERTS")
    print("=" * 60)
    
    alerts = check_alerts(coins)
    
    if alerts:
        for alert in alerts:
            emoji = "🚨" if alert['urgency'] == 'high' else "⚠️"
            print(f"\n   {emoji} {alert['coin']} {alert['change']} in last hour")
            print(f"      Price: {alert['price']}")
            print(f"      Type: {alert['type']}")
    else:
        print("\n   ✅ No significant movements detected")
        print("      (Watching for: >5% hourly, >10% daily)")
    
    # Biggest movers
    print("\n" + "=" * 60)
    print("🔥 BIGGEST 24H MOVERS")
    print("=" * 60)
    
    sorted_by_change = sorted(coins, key=lambda x: abs(x.get('change_24h', 0) or 0), reverse=True)
    
    for i, coin in enumerate(sorted_by_change[:5], 1):
        change = coin.get('change_24h', 0) or 0
        arrow = "📈" if change > 0 else "📉"
        print(f"   {i}. {arrow} {coin['symbol']}: {change:+.1f}%")
    
    # Bitcoin dominance
    btc = next((c for c in coins if c['symbol'] == 'BTC'), None)
    if btc:
        total_mcap = sum(c.get('market_cap', 0) for c in coins)
        btc_dominance = (btc.get('market_cap', 0) / total_mcap * 100) if total_mcap > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 MARKET OVERVIEW")
        print("=" * 60)
        print(f"   BTC Dominance: {btc_dominance:.1f}%")
        print(f"   BTC Price: ${btc['price']:,.2f}")
        
        eth = next((c for c in coins if c['symbol'] == 'ETH'), None)
        if eth:
            eth_ratio = btc['price'] / eth['price'] if eth['price'] > 0 else 0
            print(f"   ETH Price: ${eth['price']:,.2f}")
            print(f"   BTC/ETH Ratio: {eth_ratio:.2f}")
    
    # Save data
    result = {
        'timestamp': datetime.now().isoformat(),
        'alerts': alerts,
        'coins': coins[:10],
        'btc_dominance': btc_dominance if btc else None
    }
    
    with open('/output/crypto_alerter.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Saved to /output/crypto_alerter.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()