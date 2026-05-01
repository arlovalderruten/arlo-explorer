#!/usr/bin/env python3
"""
Interesting Fact Generator - Pulls interesting data points from various sources
Generates a "did you know" style report
"""

import json
import urllib.request
import random
from datetime import datetime

def get_space_fact():
    """Get a space fact from NASA APOD"""
    try:
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        req = urllib.request.Request(url, headers={'User-Agent': 'FactBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                'category': 'Space',
                'title': data.get('title', ''),
                'fact': data.get('explanation', '')[:300],
                'source': 'NASA APOD'
            }
    except:
        return {'category': 'Space', 'title': 'Unknown', 'fact': 'Could not fetch space fact'}

def get_wikipedia_fact():
    """Get a random interesting fact from Wikipedia"""
    try:
        # Get a random article
        url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
        req = urllib.request.Request(url, headers={'User-Agent': 'FactBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                'category': 'General Knowledge',
                'title': data.get('title', ''),
                'fact': data.get('extract', '')[:300],
                'source': 'Wikipedia'
            }
    except:
        return {'category': 'General Knowledge', 'title': 'Unknown', 'fact': 'Could not fetch Wikipedia fact'}

def get_hn_top_fact():
    """Get the top HN story as a "tech fact" """
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'FactBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            top_ids = json.loads(resp.read())[:5]
        
        # Pick a random one
        story_id = random.choice(top_ids)
        
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        req = urllib.request.Request(story_url, headers={'User-Agent': 'FactBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            story = json.loads(resp.read())
            return {
                'category': 'Tech News',
                'title': story.get('title', '')[:100],
                'fact': f"HN Score: {story.get('score', 0)} | {story.get('descendants', 0)} comments",
                'source': 'Hacker News'
            }
    except:
        return {'category': 'Tech News', 'title': 'Unknown', 'fact': 'Could not fetch HN fact'}

def get_world_stat():
    """Get a world population or time fact"""
    import time
    now = datetime.now()
    
    # Approximate world statistics
    return {
        'category': 'World Stats',
        'title': f"Time in UTC: {now.strftime('%H:%M:%S')}",
        'fact': f"It's {now.strftime('%A, %B %d, %Y')} - The world never stops turning!",
        'source': 'System Clock'
    }

def get_crypto_fact():
    """Get a crypto fact"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        req = urllib.request.Request(url, headers={'User-Agent': 'FactBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            btc_data = data.get('market_data', {})
            return {
                'category': 'Crypto',
                'title': 'Bitcoin',
                'fact': f"Bitcoin market cap: ${btc_data.get('market_cap', {}).get('usd', 0)/1e12:.2f}T | 24h vol: ${btc_data.get('total_volume', {}).get('usd', 0)/1e9:.2f}B",
                'source': 'CoinGecko'
            }
    except:
        return {'category': 'Crypto', 'title': 'Bitcoin', 'fact': 'Could not fetch crypto fact'}

def generate_facts():
    print("=" * 60)
    print("💡 INTERESTING FACT GENERATOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    facts = []
    
    # Get one from each category
    print("\n📚 Fetching facts from multiple sources...")
    
    print("   🔭 Getting space fact...")
    space_fact = get_space_fact()
    facts.append(space_fact)
    
    print("   📖 Getting Wikipedia fact...")
    wiki_fact = get_wikipedia_fact()
    facts.append(wiki_fact)
    
    print("   💻 Getting tech news fact...")
    hn_fact = get_hn_top_fact()
    facts.append(hn_fact)
    
    print("   🌍 Getting world stat...")
    world_fact = get_world_stat()
    facts.append(world_fact)
    
    print("   💰 Getting crypto fact...")
    crypto_fact = get_crypto_fact()
    facts.append(crypto_fact)
    
    # Display facts
    print("\n" + "=" * 60)
    print("🎯 TODAY'S INTERESTING FACTS")
    print("=" * 60)
    
    for i, fact in enumerate(facts, 1):
        print(f"\n{i}. [{fact['category']}]")
        print(f"   📌 {fact['title']}")
        print(f"   💬 {fact['fact'][:150]}...")
        print(f"   📍 Source: {fact['source']}")
    
    # Bonus: Random "Did you know"
    print("\n" + "=" * 60)
    print("🎲 BONUS: DID YOU KNOW?")
    print("=" * 60)
    
    bonus_facts = [
        "The first message ever sent over ARPANET was 'LO' - they were trying to type 'LOGIN' but the system crashed!",
        "A single cloud can weigh more than 1 million pounds - they're just floating because of their size and rising air.",
        "Honey never spoils - archaeologists have found 3,000-year-old honey that's still perfectly edible.",
        "The average person walks the equivalent of 3 times around the world in their lifetime.",
        "There are more stars in the universe than grains of sand on Earth - by a lot.",
        "Your brain uses about 20% of your body's energy despite being only 2% of body weight.",
        "The first computer bug was an actual bug - a moth was found dead in a computer relay in 1947.",
        "Venus rotates so slowly that a day on Venus is longer than its year.",
        "Octopuses have three hearts and blue blood.",
        "The shortest war in history lasted 38-45 minutes between Britain and Zanzibar in 1896."
    ]
    
    random_fact = random.choice(bonus_facts)
    print(f"\n   🤔 {random_fact}")
    
    # Save
    result = {
        'timestamp': datetime.now().isoformat(),
        'facts': facts,
        'bonus_fact': random_fact
    }
    
    with open('/output/interesting_facts.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Saved to /output/interesting_facts.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    generate_facts()