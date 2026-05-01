#!/usr/bin/env python3
"""
Meme Generator - Check what's trending in tech culture
Combines HN, Reddit, and generates "tech proverbs"
"""

import json
import random
from datetime import datetime

def get_trending_topics():
    """Load trending data"""
    try:
        with open('/output/trending_crossplatform.json') as f:
            return json.load(f)
    except:
        return {}

def generate_tech_proverb():
    """Generate a tech proverb based on current trends"""
    templates = [
        "The best code is the code you never have to write.",
        "In the land of bugs, the one who tests wins.",
        "A refactor in time saves nine.",
        "Those who don't read docs are doomed to repeat it.",
        "The stack overflow is strong with this one.",
        "There are only two hard things: cache invalidation and naming.",
        "Make it work, make it right, make it fast - in that order.",
        "Debugging is twice as hard as writing code. Write wisely.",
        "Any fool can write code that a computer can understand.",
        "Good code is its own best documentation.",
        "The purpose of abstracting is not to be vague, but to create the right boundary.",
        "Simple things should be simple, complex things should be possible.",
        "Talk is cheap. Show me the code.",
        "First, solve the problem. Then, write the code.",
        "Code never lies, comments sometimes do."
    ]
    return random.choice(templates)

def generate_tech_forecast():
    """Generate a funny tech forecast based on trending topics"""
    forecasts = [
        "AI will continue to amaze and confuse us equally.",
        "Rust will keep gaining popularity until the heat death of the universe.",
        "Every framework is the best framework until it isn't.",
        "The cloud will continue to be just someone else's computer.",
        "Tech bros will continue to tech bro.",
        "Documentation will remain the most underrated part of software.",
        "The merge conflict will always come at the worst time.",
        "Your tests will pass locally and fail in production.",
        "The bug is always in the code you didn't write.",
        "Dependencies will continue to be updated right before your deadline."
    ]
    return random.choice(forecasts)

def main():
    print("=" * 60)
    print("😂 TECH MEME GENERATOR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Get current data
    trending = get_trending_topics()
    topics = trending.get('topics', {}) if trending else {}
    
    print("\n🎭 BASED ON CURRENT TRENDS...")
    
    if topics:
        print(f"\n   Hot topics: {', '.join(topics.keys())}")
    
    # Generate content
    print("\n" + "=" * 60)
    print("💬 TECH PROVERB OF THE DAY")
    print("=" * 60)
    
    proverb = generate_tech_proverb()
    print(f"\n   \"{proverb}\"")
    print(f"\n   — Ancient Developer Wisdom")
    
    print("\n" + "=" * 60)
    print("🔮 TECH FORECAST")
    print("=" * 60)
    
    forecast = generate_tech_forecast()
    print(f"\n   {forecast}")
    
    print("\n" + "=" * 60)
    print("🎲 DID YOU KNOW? (Tech Edition)")
    print("=" * 60)
    
    tech_facts = [
        "The first computer virus was created in 1971 and was called 'Creeper'.",
        "The term 'bug' actually comes from a real moth found in a computer in 1947.",
        "The first ARPANET message was 'LO' - they were trying to type 'LOGIN'.",
        "QWERTY keyboard layout was designed to slow typists down (to prevent jamming).",
        "The first 1GB disk drive in 1980 weighed about 550 pounds.",
        "HTML was invented by Tim Berners-Lee in 1991.",
        "The first video game (Spacewar!) was created in 1962.",
        "Android's logo is a robot, inspired by the name 'Android'.",
        "Python was named after Monty Python, not the snake.",
        "Git was created by Linus Torvalds in 2005."
    ]
    
    fact = random.choice(tech_facts)
    print(f"\n   🤔 {fact}")
    
    # Save
    result = {
        'timestamp': datetime.now().isoformat(),
        'proverb': proverb,
        'forecast': forecast,
        'tech_fact': fact,
        'trending_topics': list(topics.keys()) if topics else []
    }
    
    with open('/output/meme_generator.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Saved to /output/meme_generator.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()