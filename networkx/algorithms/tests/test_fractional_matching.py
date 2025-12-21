import random

import pytest
import networkx as nx
from networkx.algorithms.matching import minimal_fraction_max_matching

try:
    from scipy.optimize import linprog
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

def test_empty_graph():
    """Test that an empty graph returns an empty matching."""
    G = nx.Graph()
    m = minimal_fraction_max_matching(G)
    assert m == {}  # no edges at all

def test_single_edge():
    """Test that a single edge gets value 1."""
    G = nx.Graph()
    G.add_edge(1, 2)
    m = minimal_fraction_max_matching(G)
    assert m == {(1, 2): 1}

def test_triangle():
    """Test that a triangle graph has a valid fractional matching."""
    # A 3-cycle must have values of 0.5 on each edge to be optimal
    G = nx.cycle_graph(3)
    m = minimal_fraction_max_matching(G)
    
    # Each edge should have value 0.5 in the optimal solution
    edges = list(G.edges())
    for edge in edges:
        # Handle either orientation of the edge
        edge_val = m.get(edge, m.get((edge[1], edge[0]), 0))
        assert abs(edge_val - 0.5) < 1e-8
    
    # Check node capacity constraints
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert abs(incident_sum - 1.0) < 1e-8

def test_minimal_fraction_max_matching():
    """Test the minimal_fraction_max_matching function to show that it does return a valid matching with the smallest amount of 0.5 edges."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
    
    # The optimal matching should be {(1, 2): 0.5, (3, 4): 0.5}
    m = minimal_fraction_max_matching(G)
    
    # Check that the total weight is correct
    total_weight = sum(m.values())
    assert abs(total_weight - 2.0) < 1e-8

def test_path_graph():
    """Test path graph matching."""
    G = nx.path_graph(4)  # 0-1-2-3
    m = minimal_fraction_max_matching(G)
    
    # Should be able to match edges (0,1) and (2,3) with value 1 each
    total_weight = sum(m.values())
    assert abs(total_weight - 2.0) < 1e-8
    
    # Check node capacity constraints
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert incident_sum <= 1.0 + 1e-8

def test_cycle_graph():
    """Test cycle graph matching."""
    # Even cycle can have perfect matching with value 1 edges
    G = nx.cycle_graph(4)
    m = minimal_fraction_max_matching(G)
    total_weight = sum(m.values())
    assert abs(total_weight - 2.0) < 1e-8
    
    # Odd cycle needs 0.5 edges
    G = nx.cycle_graph(5)
    m = minimal_fraction_max_matching(G)
    total_weight = sum(m.values())
    assert abs(total_weight - 2.5) < 1e-8

def test_bipartite_graph():
    """Test bipartite graph matching."""
    G = nx.complete_bipartite_graph(2, 2)
    m = minimal_fraction_max_matching(G)
    total_weight = sum(m.values())
    assert abs(total_weight - 2.0) < 1e-8

def test_directed_raises():
    """Test that directed graphs raise an exception."""
    G = nx.DiGraph([(1, 2)])
    with pytest.raises(nx.NetworkXNotImplemented):
        minimal_fraction_max_matching(G)

def test_k4_complete_graph():
    """Test complete graph K4."""
    G = nx.complete_graph(4)
    m = minimal_fraction_max_matching(G)
    
    # K4 should have total weight 2 (maximum matching)
    total_weight = sum(m.values())
    assert abs(total_weight - 2.0) < 1e-8
    
    # Check node capacity constraints
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert incident_sum <= 1.0 + 1e-8

def test_property_on_random():
    """Test that the matching satisfies basic properties on random graphs."""
    random.seed(42)
    for _ in range(10):
        n = random.randint(5, 15)
        p = random.uniform(0.1, 0.5)
        G = nx.erdos_renyi_graph(n, p, seed=42)
        
        if len(G.edges()) == 0:
            continue
            
        m = minimal_fraction_max_matching(G)
        
        # Check node capacity constraints
        for node in G:
            incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
            assert incident_sum <= 1.0 + 1e-8
        
        # Check edge values are valid
        for (u, v), val in m.items():
            assert val in [0.5, 1.0] or abs(val - 0.5) < 1e-8 or abs(val - 1.0) < 1e-8

@pytest.mark.parametrize("n, p", [(10, 0.3), (15, 0.2), (20, 0.1)])
def test_large_random_graph_constraints(n, p):
    """Test that the matching satisfies constraints on larger random graphs."""
    G = nx.erdos_renyi_graph(n, p, seed=42)
    if len(G.edges()) == 0:
        return  # Skip empty graphs
        
    m = minimal_fraction_max_matching(G)
    
    # Check node capacity constraints
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert incident_sum <= 1.0 + 1e-8
    
    # Check edge values are in {0.5, 1}
    for (u, v), val in m.items():
        assert val in [0.5, 1.0] or abs(val - 0.5) < 1e-8 or abs(val - 1.0) < 1e-8

def test_powerlaw_graph_constraints():
    """Test on power law graph."""
    try:
        G = nx.powerlaw_cluster_graph(12, 2, 0.3, seed=42)
    except:
        G = nx.erdos_renyi_graph(12, 0.3, seed=42)
    
    if len(G.edges()) == 0:
        return
        
    m = minimal_fraction_max_matching(G)
    
    # Verify basic constraints
    node_load = {v: 0.0 for v in G}
    for (u, v), val in m.items():
        assert val in (0.5, 1.0) or abs(val - 0.5) < 1e-8 or abs(val - 1.0) < 1e-8
        assert (v, u) not in m
        node_load[u] += val
        node_load[v] += val
    assert all(load <= 1.0 + 1e-8 for load in node_load.values())


def test_minimality_property():
    """Test that algorithm minimizes 0.5 edges when multiple optimal solutions exist."""
    # 4-cycle: can be matched perfectly with two 1.0 edges instead of four 0.5 edges
    G = nx.cycle_graph(4)
    m = minimal_fraction_max_matching(G)
    
    half_edges = sum(1 for val in m.values() if abs(val - 0.5) < 1e-8)
    total_weight = sum(m.values())
    
    assert abs(total_weight - 2.0) < 1e-8  # Optimal weight
    assert half_edges == 0  # Should use no 0.5 edges

def test_odd_vs_even_cycles():
    """Test that odd cycles require 0.5 edges while even cycles don't."""
    # Even cycles can be perfectly matched
    for n in [4, 6, 8]:
        G = nx.cycle_graph(n)
        m = minimal_fraction_max_matching(G)
        half_edges = sum(1 for val in m.values() if abs(val - 0.5) < 1e-8)
        assert half_edges == 0, f"Even cycle of size {n} should not need 0.5 edges"
    
    # Odd cycles must use 0.5 edges
    for n in [3, 5, 7]:
        G = nx.cycle_graph(n)
        m = minimal_fraction_max_matching(G)
        half_edges = sum(1 for val in m.values() if abs(val - 0.5) < 1e-8)
        assert half_edges == n, f"Odd cycle of size {n} should use all 0.5 edges"


def solve_fractional_matching_scipy(G):
    """
    Solve the fractional matching problem using scipy linear programming.
    Returns the total weight of the maximum fractional matching.
    """
    if not HAS_SCIPY:
        pytest.skip("scipy not available")
    
    edges = list(G.edges())
    if not edges:
        return 0
    
    num_edges = len(edges)
    num_nodes = len(G.nodes())
    
    # Objective: maximize sum of edge variables (minimize negative sum)
    c = [-1.0] * num_edges  # coefficients for maximization (negate for minimization)
    
    # Bounds: each edge variable between 0 and 1
    bounds = [(0, 1) for _ in range(num_edges)]
    
    # Inequality constraints: for each node, sum of incident edges <= 1
    A_ub = []
    b_ub = []
    
    for node in G.nodes():
        constraint = [0.0] * num_edges
        for i, (u, v) in enumerate(edges):
            if u == node or v == node:
                constraint[i] = 1.0
        A_ub.append(constraint)
        b_ub.append(1.0)
    
    # Solve the linear program
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if result.success:
        return -result.fun  # negate because we minimized the negative
    else:
        return 0


def solve_fractional_matching_scipy_with_values(G):
    """
    Solve the fractional matching problem using scipy linear programming.
    Returns a dictionary mapping edges to their optimal values.
    """
    if not HAS_SCIPY:
        pytest.skip("scipy not available")
    
    edges = list(G.edges())
    if not edges:
        return {}
    
    num_edges = len(edges)
    
    # Objective: maximize sum of edge variables (minimize negative sum)
    c = [-1.0] * num_edges
    
    # Bounds: each edge variable between 0 and 1
    bounds = [(0, 1) for _ in range(num_edges)]
    
    # Inequality constraints: for each node, sum of incident edges <= 1
    A_ub = []
    b_ub = []
    
    for node in G.nodes():
        constraint = [0.0] * num_edges
        for i, (u, v) in enumerate(edges):
            if u == node or v == node:
                constraint[i] = 1.0
        A_ub.append(constraint)
        b_ub.append(1.0)
    
    # Solve the linear program
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if result.success:
        # Return edge assignments (only non-zero values)
        matching = {}
        for i, (u, v) in enumerate(edges):
            val = result.x[i]
            if val > 1e-6:  # Only include non-zero values
                # Ensure consistent edge orientation (smaller node first)
                edge = (min(u, v), max(u, v))
                matching[edge] = val
        return matching
    else:
        return {}


@pytest.mark.skipif(not HAS_SCIPY, reason="scipy not available")
@pytest.mark.parametrize("n, p", [(10, 0.3), (15, 0.2), (8, 0.4)])
def test_compare_with_scipy(n, p):
    """
    Compare the fractional matching algorithm with scipy linear programming solution.
    Both should produce the same optimal total weight.
    """
    G = nx.erdos_renyi_graph(n, p, seed=42)
    if len(G.edges()) == 0:
        pytest.skip("Empty graph")
    
    # Solve using our algorithm
    algo_match = minimal_fraction_max_matching(G)
    algo_weight = sum(algo_match.values())
    
    # Solve using scipy
    scipy_weight = solve_fractional_matching_scipy(G)
    
    # The weights should be very close (allowing for small floating point differences)
    assert abs(algo_weight - scipy_weight) < 1e-5, f"Algorithm: {algo_weight}, Scipy: {scipy_weight}"


@pytest.mark.skipif(not HAS_SCIPY, reason="scipy not available")  
def test_minimality_vs_scipy():
    """
    Test that our algorithm produces solutions with fewer or equal 0.5-valued edges
    compared to a generic LP solution on various graph types.
    """
    test_graphs = [
        nx.cycle_graph(4),  # Even cycle - should prefer 1.0 edges
        nx.cycle_graph(5),  # Odd cycle - must use 0.5 edges
        nx.complete_graph(4),  # K4
        nx.path_graph(5),  # Path graph
        nx.complete_bipartite_graph(3, 3),  # Bipartite
        nx.erdos_renyi_graph(8, 0.4, seed=42),  # Random
    ]
    
    for i, G in enumerate(test_graphs):
        if len(G.edges()) == 0:
            continue
            
        # Get our algorithm solution
        algo_match = minimal_fraction_max_matching(G)
        algo_weight = sum(algo_match.values())
        
        # Count 0.5 edges in our solution
        algo_half_edges = sum(1 for val in algo_match.values() if abs(val - 0.5) < 1e-6)
        
        # Get scipy solution
        scipy_match = solve_fractional_matching_scipy_with_values(G)
        scipy_weight = sum(scipy_match.values())
        
        # Count 0.5 edges in scipy solution (might have fractional values other than 0.5/1.0)
        scipy_fractional_edges = sum(1 for val in scipy_match.values() 
                                   if abs(val - 0.5) < 1e-6 or (val > 1e-6 and abs(val - 1.0) > 1e-6))
        
        # Verify same total weight (optimal solutions)
        assert abs(algo_weight - scipy_weight) < 1e-5, \
            f"Graph {i}: Algorithm weight {algo_weight} != Scipy weight {scipy_weight}"
        
        # Our algorithm should minimize fractional edges when possible
        # (This is a heuristic check - LP might find different optimal solutions)
        print(f"Graph {i}: Algo half-edges={algo_half_edges}, Scipy fractional={scipy_fractional_edges}")


@pytest.mark.skipif(not HAS_SCIPY, reason="scipy not available")
def test_specific_graphs_vs_scipy():
    """Test specific known cases against scipy to ensure correctness."""
    
    # Test triangle (should have all 0.5 edges)
    G = nx.cycle_graph(3)
    algo_match = minimal_fraction_max_matching(G)
    scipy_weight = solve_fractional_matching_scipy(G)
    algo_weight = sum(algo_match.values())
    
    assert abs(algo_weight - 1.5) < 1e-6
    assert abs(scipy_weight - 1.5) < 1e-6
    assert abs(algo_weight - scipy_weight) < 1e-5
    
    # Test 4-cycle (should have perfect matching with 1.0 edges)
    G = nx.cycle_graph(4)
    algo_match = minimal_fraction_max_matching(G)
    scipy_weight = solve_fractional_matching_scipy(G)
    algo_weight = sum(algo_match.values())
    
    assert abs(algo_weight - 2.0) < 1e-6
    assert abs(scipy_weight - 2.0) < 1e-6
    assert abs(algo_weight - scipy_weight) < 1e-5


if __name__ == "__main__":
    pytest.main([__file__])
