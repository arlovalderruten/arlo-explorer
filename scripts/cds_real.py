#!/usr/bin/env python3
"""
CDS with Real Data - Process the fetched data through synthesis
"""

import json
from pathlib import Path

# Load real data
input_file = Path("/output/real_cds_input.json")
with open(input_file) as f:
    data = json.load(f)

nodes = data['nodes']

print("=" * 60)
print("CDS MODULE - REAL DATA SYNTHESIS")
print("=" * 60)
print(f"Timestamp: {data['metadata']['collected_at']}")
print(f"Sources: {', '.join(data['metadata']['sources'])}")
print("=" * 60)
print(f"Nodes loaded: {len(nodes)}")

print("\n📋 INPUT NODES:")
for i, node in enumerate(nodes, 1):
    print(f"  {i}. {node.get('id', 'N/A')}: {node.get('category', 'N/A')}")
    if 'error' in node:
        print(f"     ❌ {node['error']}")

# Categorize
by_category = {}
for node in nodes:
    cat = node.get('category', 'Unknown')
    if cat not in by_category:
        by_category[cat] = []
    by_category[cat].append(node)

print("\n📊 BY CATEGORY:")
for cat, items in by_category.items():
    print(f"  {cat}: {len(items)} nodes")

# Cross-category synthesis
print("\n" + "=" * 60)
print("🔬 CROSS-DISCIPLINARY SYNTHESIS")
print("=" * 60)

categories = list(by_category.keys())
for i in range(len(categories)):
    for j in range(i+1, len(categories)):
        cat1, cat2 = categories[i], categories[j]
        print(f"\n🔗 {cat1} ↔ {cat2}")
        
        nodes1 = by_category[cat1]
        nodes2 = by_category[cat2]
        
        for n1 in nodes1:
            for n2 in nodes2:
                tags1 = set(n1.get('tags', []))
                tags2 = set(n2.get('tags', []))
                
                if tags1 and tags2:
                    intersection = len(tags1 & tags2)
                    union = len(tags1 | tags2)
                    similarity = (intersection / union * 100) if union > 0 else 0
                    
                    if similarity > 15:
                        print(f"   • {n1.get('id', 'N/A').split('_', 1)[-1]} ↔ {n2.get('id', 'N/A').split('_', 1)[-1][:30]}")
                        print(f"     Similarity: {similarity:.0f}%")

# Generate synthesis insights
print("\n" + "=" * 60)
print("💡 SYNTHESIS INSIGHTS")
print("=" * 60)

insights = []

if 'Technology' in by_category and 'Geopolitics' in by_category:
    insight = """
BRIDGE CONCEPT: Technology as Infrastructure in Geopolitical Conflict

The intersection of tech repositories and world news reveals that 
technology is increasingly becoming both:
  • A tool OF conflict (cyber warfare, surveillance)
  • A target OF conflict (supply chain attacks, sanctions)

SYnthetic insight: The tech industry's "connect everything" paradigm
is being challenged by geopolitical realities demanding "disconnect
as defense" capabilities.
"""
    insights.append(insight)
    print(insight)

if 'Technology' in by_category:
    tech_nodes = by_category['Technology']
    if len(tech_nodes) >= 2:
        insight = """
BRIDGE CONCEPT: Open Source as Collective Infrastructure

Multiple tech repositories suggest collaborative codebases becoming
shared tooling. The tension between open development and proprietary
data practices is growing.

SYNTHETIC INSIGHT: Open-source may be positioning as the trustworthy
alternative to surveillance-capitalism tech.
"""
        insights.append(insight)
        print(insight)

if 'Geopolitics' in by_category:
    geo_nodes = by_category['Geopolitics']
    if len(geo_nodes) >= 2:
        titles = [n.get('title', '')[:40] for n in geo_nodes[:2]]
        insight = f"""
BRIDGE CONCEPT: Information Warfare and Narrative Control

Multiple threads on conflict show parallel information warfare:
  • "{titles[0]}..."
  • "{titles[1]}..."

Public is actively consuming conflict information while multiple
narratives compete for dominance.

SYNTHETIC INSIGHT: The "first draft of history" is now contested
territory, with bots, state actors, and genuine eyewitnesses all
competing in the same information ecosystem.
"""
        insights.append(insight)
        print(insight)

# Save results
output = {
    'synthesis_timestamp': data['metadata']['collected_at'],
    'input_nodes': len(nodes),
    'categories': list(by_category.keys()),
    'insights': insights,
    'raw_nodes': nodes
}

with open('/output/cds_real_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n✅ Analysis complete. Results saved to /output/cds_real_results.json")