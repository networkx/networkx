"""
Test script to reproduce issue #8271 with densest_subgraph FISTA algorithm.

The issue is that when nodes have labels that are not 0-indexed (like [0,1,3], [1,2,3], or ["abc"]),
the FISTA algorithm incorrectly maps nodes to indices, causing IndexError or incorrect results.
"""

import sys
import networkx as nx
from networkx.algorithms import approximation

# Check numpy
try:
    import numpy as np
except ImportError:
    print("ERROR: NumPy not installed. Please install it: pip install numpy")
    sys.exit(1)

def test_case_1_missing_label():
    """Test with missing node labels [0, 1, 3] - 2 is missing"""
    print("=" * 60)
    print("Test Case 1: Node labels [0, 1, 3] (missing 2)")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 3), (0, 3)])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print(f"Expected: Should handle non-sequential labels")
    
    try:
        density, subgraph = approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"✓ Success - Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"✗ Failed with error: {type(e).__name__}: {e}")
        return False

def test_case_2_offset_labels():
    """Test with offset node labels [1, 2, 3]"""
    print("\n" + "=" * 60)
    print("Test Case 2: Node labels [1, 2, 3] (offset by 1)")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (1, 3)])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print(f"Expected: Should handle offset labels")
    
    try:
        density, subgraph = approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"✓ Success - Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"✗ Failed with error: {type(e).__name__}: {e}")
        return False

def test_case_3_string_labels():
    """Test with string node labels ["a", "b", "c"]"""
    print("\n" + "=" * 60)
    print("Test Case 3: Node labels ['a', 'b', 'c'] (string labels)")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edges_from([("a", "b"), ("b", "c"), ("a", "c")])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print(f"Expected: Should handle string labels")
    
    try:
        density, subgraph = approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"✓ Success - Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"✗ Failed with error: {type(e).__name__}: {e}")
        return False

def test_case_4_baseline_zero_indexed():
    """Baseline test with sequential 0-indexed nodes (should work)"""
    print("\n" + "=" * 60)
    print("Test Case 4: Node labels [0, 1, 2] (sequential from 0)")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (0, 2)])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print(f"Expected: Should work (baseline)")
    
    try:
        density, subgraph = approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"✓ Success - Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"✗ Failed with error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("\nNetworkX Issue #8271: densest_subgraph with non-sequential node labels")
    print("Root Cause: enumerate(G) assumes sequential 0-indexed node labels")
    print()
    
    results = []
    results.append(("Baseline (0,1,2)", test_case_4_baseline_zero_indexed()))
    results.append(("Missing label", test_case_1_missing_label()))
    results.append(("Offset labels", test_case_2_offset_labels()))
    results.append(("String labels", test_case_3_string_labels()))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    exit(0 if all_passed else 1)
