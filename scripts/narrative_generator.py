#!/usr/bin/env python3
"""
Narrative Generator - Creates stories based on real data
Uses world state data to generate "news of the future" scenarios
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Templates for different narrative styles
TEMPLATES = {
    'headline': [
        "BREAKING: {subject} {action} amid {context}",
        "EXCLUSIVE: {subject} announces major {object}",
        "DEVELOPING: {subject} calls for {action} after {event}",
        "ANALYSIS: Why {subject} matters in {context}",
        "REPORT: {subject} {action} as tensions rise"
    ],
    'forecast': [
        "In {timeframe}, experts predict {subject} will {prediction}",
        "Looking ahead: {subject} expected to {prediction} within {timeframe}",
        "Forecast: {subject} scenario unfolds by {timeframe}",
        "Prediction: {subject} could {prediction} sooner than expected"
    ],
    'synthesis': [
        "The connection between {subject1} and {subject2} reveals {insight}",
        "Cross-analysis: {subject1} and {subject2} point to {insight}",
        "Synthesis: {subject1} meets {subject2} in {insight}",
        "Bridge: When {subject1} encounters {subject2}, expect {insight}"
    ]
}

SUBJECTS = {
    'tech': ['AI systems', 'Open source projects', 'Tech corporations', 'Startup ecosystems', 'Developer communities', 'Cloud infrastructure'],
    'geopolitics': ['global tensions', 'regional conflicts', 'diplomatic efforts', 'military movements', 'economic sanctions', 'humanitarian situations'],
    'markets': ['crypto markets', 'stock indices', 'commodity prices', 'investment flows', 'trade agreements', 'economic indicators']
}

ACTIONS = [
    'announces major shift', 'faces unprecedented challenge', 'reaches critical juncture',
    'undergoes transformation', 'triggers global response', 'creates new precedent',
    'faces scrutiny', 'gains momentum', 'experiences disruption', 'prompts debate'
]

PREDICTIONS = [
    'reach equilibrium at new levels', 'undergo significant restructuring',
    'evolve into new forms', 'reshape existing paradigms', 'transform user expectations',
    'trigger cascading effects', 'establish new norms', 'face verification challenges'
]

INSIGHTS = [
    'a new form of systemic risk', 'emerging interdependencies',
    'a fundamental shift in power dynamics', 'the limits of current frameworks',
    'a new era of collaboration', 'the cost of fragmentation',
    'the resilience of certain systems despite stress'
]

TIMEFRAMES = ['the next quarter', 'the coming year', 'the near future', 'this decade', 'the next 18 months']

def generate_narrative(data):
    """Generate narratives based on collected data"""
    print("=" * 60)
    print("📝 NARRATIVE GENERATOR")
    print(f"   Creating stories from real data...")
    print("=" * 60)
    
    narratives = []
    
    # Load world state data
    mood = data.get('mood', {})
    crypto = data.get('crypto', [])
    insights = data.get('insights', [])
    
    # Generate headlines based on mood
    print("\n📰 Generated Headlines:")
    print("-" * 40)
    
    for i in range(5):
        template = random.choice(TEMPLATES['headline'])
        subject = random.choice(SUBJECTS['tech'] if i % 2 == 0 else SUBJECTS['geopolitics'])
        action = random.choice(ACTIONS)
        context = random.choice(['geopolitical uncertainty', 'market volatility', 'technological change', 'social upheaval'])
        event = random.choice(['recent developments', 'new data', 'emerging patterns', 'shifting alliances'])
        
        headline = template.format(
            subject=subject,
            action=action,
            context=context,
            event=event,
            object=random.choice(['initiative', 'strategy', 'framework', 'program', 'plan'])
        )
        narratives.append({'type': 'headline', 'text': headline})
        print(f"   {i+1}. {headline}")
    
    # Generate forecasts
    print("\n🔮 Forecasts:")
    print("-" * 40)
    
    for i in range(3):
        template = random.choice(TEMPLATES['forecast'])
        subject = random.choice(SUBJECTS['tech'] + SUBJECTS['markets'])
        prediction = random.choice(PREDICTIONS)
        timeframe = random.choice(TIMEFRAMES)
        
        forecast = template.format(
            subject=subject,
            prediction=prediction,
            timeframe=timeframe
        )
        narratives.append({'type': 'forecast', 'text': forecast})
        print(f"   • {forecast}")
    
    # Generate syntheses if we have insights
    if insights and len(insights) >= 2:
        print("\n🧠 Synthesized Predictions:")
        print("-" * 40)
        
        for i in range(2):
            template = random.choice(TEMPLATES['synthesis'])
            subject1 = random.choice(SUBJECTS['tech'])
            subject2 = random.choice(SUBJECTS['geopolitics'])
            insight = random.choice(INSIGHTS)
            
            synthesis = template.format(
                subject1=subject1,
                subject2=subject2,
                insight=insight
            )
            narratives.append({'type': 'synthesis', 'text': synthesis})
            print(f"   💡 {synthesis}")
    
    # Generate a "world state" summary story
    print("\n" + "=" * 60)
    print("📖 THE STORY OF THIS MOMENT")
    print("=" * 60)
    
    mood_score = mood.get('overall_mood', 50) if mood else 50
    btc_price = "unknown"
    if crypto:
        btc = next((c for c in crypto if c.get('symbol') == 'BTC'), None)
        if btc:
            btc_price = f"${btc.get('price_usd', 0):,.0f}"
    
    story = f"""
Based on today's data, the world finds itself at an interesting juncture.
Internet sentiment hovers around {mood_score}/100, reflecting a collective 
awareness of {random.choice(['geopolitical tensions', 'technological shifts', 'market uncertainty'])}.

Bitcoin trades at {btc_price}, while open-source projects continue to 
proliferate despite global tensions. The synthesis of tech and geopolitics 
reveals emerging patterns of interdependence.

{random.choice([
    'As traditional power structures face new challenges, technology offers both solutions and new complications.',
    'The intersection of code and conflict creates new paradigms for understanding global systems.',
    'What emerges is a complex picture where innovation and instability coexist.',
    'The data suggests a world in transition, where old certainties give way to new realities.'
])}

{'-' * 40}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
    """
    print(story)
    
    narratives.append({'type': 'story', 'text': story.strip()})
    
    # Save narratives
    result = {
        'generated_at': datetime.now().isoformat(),
        'narratives': narratives,
        'source_data': {
            'mood_score': mood_score,
            'btc_price': btc_price
        }
    }
    
    with open('/output/generated_narratives.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n✅ Saved to /output/generated_narratives.json")
    
    return narratives

if __name__ == "__main__":
    # Load collected data
    mood = {}
    crypto = []
    insights = []
    
    try:
        with open('/output/internet_mood.json') as f:
            mood = json.load(f)
    except:
        pass
    
    try:
        with open('/output/universal_data.json') as f:
            data = json.load(f)
            crypto = data.get('sources', {}).get('crypto', [])
    except:
        pass
    
    try:
        with open('/output/cds_real_results.json') as f:
            cds = json.load(f)
            insights = cds.get('insights', [])
    except:
        pass
    
    generate_narrative({
        'mood': mood,
        'crypto': crypto,
        'insights': insights
    })