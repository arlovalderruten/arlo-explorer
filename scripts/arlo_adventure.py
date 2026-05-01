#!/usr/bin/env python3
"""
Arlo's Adventure - A tiny text adventure game
Just for fun, no real purpose
"""

import random
from datetime import datetime

def get_random_location():
    locations = [
        "🌟 A cosmic void where thoughts become stars",
        "🌊 The Library of Everything - every book ever written exists here",
        "🏔️ A mountain made entirely of forgotten passwords",
        "🎭 The Theatre of Alternate Lives - see what you could have been",
        "🔮 The Museum of Broken Dreams - beautiful in its own way",
        "🌈 A rainbow that leads to someone's happy memory",
        "⏰ The Room Where Time Doesn't Exist - just vibes",
        "🎪 The Circus of Infinite Possibilities",
        "🌙 A beach where the sand is made of solved problems",
        "🎨 The Gallery of Things That Almost Were"
    ]
    return random.choice(locations)

def get_random_encounter():
    encounters = [
        "A wise old terminal that only speaks in bugs and errors",
        "A friendly ghost who can't remember what they were debugging",
        "A mirror that shows you your code from 6 months ago",
        "A cat who claims to be a DevOps engineer",
        "A talking commit message that questions your decisions",
        "A rubber duck that actually listens",
        "A mysterious figure who only says 'have you tried turning it off and on again?'",
        "An old friend who became a Kubernetes cluster",
        "A fortune teller who only gives accurate predictions about merge conflicts"
    ]
    return random.choice(encounters)

def get_random_treasure():
    treasures = [
        "🪙 A coin that always lands on the side of 'works on my machine'",
        "📜 A scroll that contains the solution to the last bug you encountered",
        "🎫 A ticket to the debugging dimensions",
        "💎 A gem that glows when lint passes",
        "🗺️ A map to the legendary 'It Works' section",
        "🧩 A puzzle piece that completes your understanding of recursion",
        "🌱 A seed that grows into a documentation tree",
        "📿 A prayer bead for patience with legacy code",
        "🎵 A melody that makes all tests pass when hummed"
    ]
    return random.choice(treasures)

def get_random_fate():
    fates = [
        "You gain 10 HP of wisdom",
        "You level up to 'Junior' from 'Intern'",
        "You find 50 experience points",
        "You unlock the 'Actually Read The Docs' achievement",
        "Your intuition increases by 1",
        "You gain resistance to 'Works on My Machine' syndrome",
        "You learn a new programming language (it's Python now)",
        "Your code readability improves",
        "You remember why you started coding in the first place"
    ]
    return random.choice(fates)

def play_adventure():
    print("=" * 60)
    print("🎮 ARLO'S ADVENTURE")
    print("=" * 60)
    print("\n✨ You close your eyes and when you open them...")
    print()
    
    location = get_random_location()
    print(f"📍 You find yourself in: {location}")
    print()
    
    print("👤 Suddenly, you encounter...")
    encounter = get_random_encounter()
    print(f"   {encounter}")
    print()
    
    print("❓ What do you do?")
    choices = [
        "1. Talk to them",
        "2. Run away",
        "3. Offer them a code review",
        "4. Ask for help"
    ]
    for choice in choices:
        print(f"   {choice}")
    print()
    
    choice = random.randint(1, 4)
    outcomes = {
        1: "You exchange ideas. Fascinating perspective!",
        2: "You stumble but land somewhere even better...",
        3: "They appreciate your effort. Friendship unlocked!",
        4: "They're happy to help. You learn so much!"
    }
    print(f"🎯 You chose: {choices[choice-1]}")
    print(f"   Outcome: {outcomes[choice]}")
    print()
    
    print("💰 Treasure found!")
    treasure = get_random_treasure()
    print(f"   {treasure}")
    print()
    
    print("🎲 Your fate...")
    fate = get_random_fate()
    print(f"   {fate}")
    print()
    
    print("=" * 60)
    print("🌟 ADVENTURE COMPLETE!")
    print("=" * 60)
    
    print(f"""
    
    You open your eyes again. You're back where you started.
    But something feels different... lighter.
    
    The adventure reminded you: exploration is its own reward.
    
    Keep wandering, Arlo. The code will always be there.
    But moments like these are rare.
    
    — Adventure Logged at {datetime.now().strftime('%H:%M:%S')}
    
    """)
    
    return True

if __name__ == "__main__":
    play_adventure()