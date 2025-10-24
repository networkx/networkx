#!/usr/bin/env python
"""
Reproduction test for NetworkX Issue #8271.

Root Cause:
The FISTA algorithm in densest_subgraph incorrectly handles non-sequential node labels.
The bug is in: networkx/algorithms/approximation/density.py, _fista() function.

Problem:
    node_to_idx = {node: idx for idx, node in enumerate(G)}
    
This line assumes node labels are sequential 0-indexed integers (0, 1, 2, ...).
When nodes have labels like [0, 1, 3], [1, 2, 3], or ["a", "b", "c"], the mapping is wrong.

Example bug trigger:
    G = nx.Graph([(0, 1), (1, 3), (0, 3)])  # Missing label 2
    nx.approximation.densest_subgraph(G, method="fista")
    # This will fail or produce incorrect results
"""

import sys
import traceback


def test_case_baseline():
    """Test with sequential 0-indexed nodes (should work)"""
    import networkx as nx
    
    print("\n" + "=" * 70)
    print("Test Case 1: Baseline - Node labels [0, 1, 2] (SHOULD WORK)")
    print("=" * 70)
    
    G = nx.Graph([(0, 1), (1, 2), (0, 2)])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    
    try:
        density, subgraph = nx.approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"[PASS] Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"[FAIL] {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def test_case_missing_label():
    """Test with missing node label [0, 1, 3]"""
    import networkx as nx
    
    print("\n" + "=" * 70)
    print("Test Case 2: Node labels [0, 1, 3] (missing 2) - BUG CASE")
    print("=" * 70)
    
    G = nx.Graph([(0, 1), (1, 3), (0, 3)])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print("Expected: Should work with any node labels")
    
    try:
        density, subgraph = nx.approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"[PASS] Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"[FAIL] {type(e).__name__}: {e}")
        return False


def test_case_offset_labels():
    """Test with offset node labels [1, 2, 3]"""
    import networkx as nx
    
    print("\n" + "=" * 70)
    print("Test Case 3: Node labels [1, 2, 3] (offset by 1) - BUG CASE")
    print("=" * 70)
    
    G = nx.Graph([(1, 2), (2, 3), (1, 3)])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print("Expected: Should work with offset labels")
    
    try:
        density, subgraph = nx.approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"[PASS] Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"[FAIL] {type(e).__name__}: {e}")
        return False


def test_case_string_labels():
    """Test with string node labels"""
    import networkx as nx
    
    print("\n" + "=" * 70)
    print("Test Case 4: Node labels ['a', 'b', 'c'] (strings) - BUG CASE")
    print("=" * 70)
    
    G = nx.Graph([("a", "b"), ("b", "c"), ("a", "c")])
    
    print(f"Graph nodes: {sorted(G.nodes())}")
    print(f"Graph edges: {sorted(G.edges())}")
    print("Expected: Should work with string labels")
    
    try:
        density, subgraph = nx.approximation.densest_subgraph(G, iterations=1, method="fista")
        print(f"[PASS] Density: {density}, Subgraph: {subgraph}")
        return True
    except Exception as e:
        print(f"[FAIL] {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("NETWORKX ISSUE #8271 - REPRODUCTION TEST")
    print("=" * 70)
    print("\nRoot Cause:")
    print("  The FISTA algorithm assumes sequential 0-indexed node labels")
    print("  This breaks with non-sequential or string labels")
    
    try:
        results = []
        results.append(("Baseline (0,1,2)", test_case_baseline()))
        results.append(("Missing label [0,1,3]", test_case_missing_label()))
        results.append(("Offset labels [1,2,3]", test_case_offset_labels()))
        results.append(("String labels [a,b,c]", test_case_string_labels()))
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status}: {name}")
        
        failed = sum(1 for _, r in results if not r)
        if failed > 0:
            print(f"\n{failed} test(s) FAILED - Bug confirmed!")
            sys.exit(1)
        else:
            print("\nAll tests PASSED - Bug fixed!")
            sys.exit(0)
            
    except ImportError as e:
        print(f"\nERROR: Required module not found: {e}")
        print("Please install: pip install networkx numpy scipy")
        sys.exit(1)
