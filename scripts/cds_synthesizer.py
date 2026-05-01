import json
from datetime import datetime

# Conceptual mapping table - maps keywords to abstract categories
CONCEPTUAL_CATEGORIES = {
    # System Instability concepts
    "Supply Disruption": "System Instability",
    "Oil Price": "System Instability",
    "Strait of Hormuz": "System Instability",
    "Inflation": "System Instability",
    "Consumer Spending": "System Instability",
    "Tax Cuts": "System Instability",
    
    # Accountability concepts
    "Purdue Pharma": "Accountability Gap",
    "Criminal Law": "Accountability Gap",
    "Corporate Liability": "Accountability Gap",
    
    # Risk propagation concepts
    "Financial Settlement": "Risk Propagation",
    "No Incarceration": "Risk Propagation",
}

def map_to_concept(keyword: str) -> str:
    """Map a keyword to its abstract conceptual category."""
    return CONCEPTUAL_CATEGORIES.get(keyword, None)

def calculate_conceptual_similarity(node_a: dict, node_b: dict) -> dict:
    """
    Calculate similarity between two nodes based on conceptual categories.
    Returns a dict with similarity score and shared concepts.
    """
    # Extract concepts for node A
    concepts_a = set()
    for kw in node_a.get('keywords', []):
        concept = map_to_concept(kw)
        if concept:
            concepts_a.add(concept)
    
    # Extract concepts for node B
    concepts_b = set()
    for kw in node_b.get('keywords', []):
        concept = map_to_concept(kw)
        if concept:
            concepts_b.add(concept)
    
    # Find overlap
    shared_concepts = concepts_a & concepts_b
    all_concepts = concepts_a | concepts_b
    
    # Calculate similarity score (Jaccard-like)
    if all_concepts:
        similarity = len(shared_concepts) / len(all_concepts)
    else:
        similarity = 0.0
    
    return {
        'node_a_id': node_a['node_id'],
        'node_b_id': node_b['node_id'],
        'similarity_score': similarity,
        'shared_concepts': list(shared_concepts),
        'all_concepts_a': list(concepts_a),
        'all_concepts_b': list(concepts_b),
    }

def generate_bridge_concept(nodes: list) -> dict:
    """
    Analyze multiple nodes to generate a unifying abstract concept (the Bridge).
    This is the core synthesis engine.
    """
    if len(nodes) < 2:
        return {'bridge': None, 'explanation': 'Need at least 2 nodes for synthesis'}
    
    # Calculate pairwise similarities
    similarity_results = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            sim = calculate_conceptual_similarity(nodes[i], nodes[j])
            similarity_results.append(sim)
    
    # Find the highest similarity pair
    best_match = max(similarity_results, key=lambda x: x['similarity_score'])
    
    # Find all shared concepts across all nodes
    all_concepts = set()
    for node in nodes:
        for kw in node.get('keywords', []):
            concept = map_to_concept(kw)
            if concept:
                all_concepts.add(concept)
    
    # Generate the bridge concept based on shared themes
    bridge = None
    explanation = None
    
    if 'System Instability' in all_concepts and 'Accountability Gap' in all_concepts:
        bridge = "Systemic Failure Without Accountability"
        explanation = (
            "When system instability (energy shocks, inflation) meets accountability gaps "
            "(corporate liability failures), the result is a compound systemic risk where "
            "the originating cause is never fully addressed."
        )
    elif len(all_concepts) > 1:
        bridge = f"Cross-Domain Risk Pattern: {', '.join(all_concepts)}"
        explanation = (
            f"Multiple conceptual domains ({', '.join(all_concepts)}) converge to reveal "
            "a pattern that none of the individual domains could explain alone."
        )
    else:
        bridge = "Emerging Pattern"
        explanation = "Insufficient conceptual overlap detected for robust synthesis."
    
    return {
        'bridge': bridge,
        'explanation': explanation,
        'similarity_results': similarity_results,
        'all_detected_concepts': list(all_concepts),
        'best_pair': best_match,
    }

def run_cds_synthesis(input_file_path: str):
    """
    Enhanced Cross-Disciplinary Synthesis Module.
    Uses conceptual mapping instead of keyword matching to find bridges between domains.
    """
    print("=" * 60)
    print("CDS MODULE - CONCEPTUAL SYNTHESIS ENGINE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Input: {input_file_path}")
    print("-" * 60)
    
    # Load data
    try:
        with open(input_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Input file not found.")
        return None
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON format.")
        return None
    
    print(f"Nodes loaded: {len(data)}")
    for node in data:
        print(f"  - {node['node_id']}: {node['primary_concept']}")
    print()
    
    # Run synthesis
    result = generate_bridge_concept(data)
    
    print("=" * 60)
    print("SYNTHESIS RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 BRIDGE CONCEPT: {result['bridge']}")
    print(f"\n📝 EXPLANATION:")
    print(f"   {result['explanation']}")
    
    print(f"\n🔍 CONCEPTUAL ANALYSIS:")
    print(f"   Detected categories: {', '.join(result['all_detected_concepts'])}")
    
    print(f"\n📊 PAIRWISE SIMILARITY SCORES:")
    for sim in result['similarity_results']:
        print(f"   {sim['node_a_id']} ↔ {sim['node_b_id']}: {sim['similarity_score']:.2%}")
        if sim['shared_concepts']:
            print(f"      Shared: {', '.join(sim['shared_concepts'])}")
    
    print("\n" + "=" * 60)
    
    return result

if __name__ == "__main__":
    mock_file = "input/mock_cds_input.json"
    run_cds_synthesis(mock_file)