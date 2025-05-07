import math
import random
import pulp  # You may need to install this: pip install pulp

import pytest
import networkx as nx
from networkx.algorithms.matching import fractional_matching

def test_empty_graph():
    """Test that an empty graph returns an empty matching."""
    G = nx.Graph()
    m = fractional_matching(G)
    assert m == {}  # no edges at all

def test_single_edge():
    """Test that a single edge gets value 1."""
    G = nx.Graph()
    G.add_edge(1, 2)
    m = fractional_matching(G)
    assert m == {(1, 2): 1}

def test_triangle():
    """Test that a triangle graph has a valid fractional matching."""
    # A 3-cycle must have values of 0.5 on each edge to be optimal
    G = nx.cycle_graph(3)
    m = fractional_matching(G)
    
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

def test_path_graph():
    """Test a simple path graph where optimal matching is known."""
    # A path of length 3 (4 nodes) should have alternating 1s
    G = nx.path_graph(4)  # 0-1-2-3
    m = fractional_matching(G)
    
    # Optimal solution should be matching edges 0-1 and 2-3
    # or equivalently, edges 1-2 with value 1
    total_weight = sum(m.values())
    assert abs(total_weight - 2) < 1e-8
    
    # Each node should have ≤ 1 total incident edge weight
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert incident_sum <= 1 + 1e-8

def test_cycle_graph():
    """Test a cycle graph with even number of nodes."""
    # A cycle with even length should have a perfect matching
    G = nx.cycle_graph(6)
    m = fractional_matching(G)
    
    # Total weight should be n/2 for perfect matching
    total_weight = sum(m.values())
    assert abs(total_weight - 3) < 1e-8
    
    # Each node should have exactly 1 incident edge weight
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert abs(incident_sum - 1.0) < 1e-8

def test_bipartite_graph():
    """Test a complete bipartite graph."""
    # K3,3 should have a perfect matching
    G = nx.complete_bipartite_graph(3, 3)
    m = fractional_matching(G)
    
    # Total weight should be min(left_size, right_size)
    total_weight = sum(m.values())
    assert abs(total_weight - 3) < 1e-8

def test_directed_raises():
    """Test that directed graphs raise appropriate exceptions."""
    D = nx.DiGraph([(1, 2)])
    with pytest.raises(nx.NetworkXNotImplemented):
        fractional_matching(D)

def test_k4_complete_graph():
    """Test K4 complete graph which requires fractional values."""
    # K4 requires fractional matching for optimality
    G = nx.complete_graph(4)
    m = fractional_matching(G)
    
    # Optimal solution should have total weight of 2
    total_weight = sum(m.values())
    assert abs(total_weight - 2) < 1e-8
    
    # In the optimal solution, all edges should have value 1/3
    # or a different pattern with sum 2 that satisfies constraints
    for node in G:
        incident_sum = sum(val for (u, v), val in m.items() if u == node or v == node)
        assert abs(incident_sum - 1.0) < 1e-8

def test_property_on_random():
    """Test with small random graphs and verify constraints."""
    for _ in range(10):
        G = nx.gnp_random_graph(5, 0.5, seed=42)
        m = fractional_matching(G)
        
        # Check fractional constraints
        for node in G:
            # Sum of weights incident to each node must be ≤ 1
            incident_sum = sum(m.get((u, v), m.get((v, u), 0)) for u, v in G.edges(node))
            assert incident_sum <= 1 + 1e-8
        
        # Check that edge values are only 0, 0.5, or 1
        for val in m.values():
            assert abs(val - 0.5) < 1e-8 or abs(val - 1.0) < 1e-8

# --------------------------------------------------------------------
# 1. Larger random graphs — verify constraints only (fast, O(E)).

@pytest.mark.parametrize(
    "n, p", [(50, 0.08), (120, 0.04), (250, 0.02)]
)
def test_large_random_graph_constraints(n, p):
    """On moderately large graphs the solution must still satisfy
    0 ≤ x_e ≤ 1 and Σ_e incident to v x_e ≤ 1 for every vertex."""
    G = nx.fast_gnp_random_graph(n, p, seed=42)
    match = fractional_matching(G)

    # Check edge values and build per-node sums
    node_load = {v: 0.0 for v in G}
    for (u, v), val in match.items():
        # Values can only be 0.5 or 1 (never store 0)
        assert val in (0.5, 1.0) or abs(val - 0.5) < 1e-8 or abs(val - 1.0) < 1e-8
        # Only store one orientation
        assert (v, u) not in match
        node_load[u] += val
        node_load[v] += val

    # Every vertex load ≤ 1
    assert all(load <= 1.0 + 1e-8 for load in node_load.values())


@pytest.mark.slow
def test_powerlaw_graph_constraints():
    """Stress the solver on a 1,000-node graph but only check feasibility."""
    G = nx.powerlaw_cluster_graph(1000, 3, 0.1, seed=7)
    frac = fractional_matching(G)

    # Quick feasibility scan
    node_load = {v: 0.0 for v in G}
    for (u, v), val in frac.items():
        assert val in (0.5, 1.0) or abs(val - 0.5) < 1e-8 or abs(val - 1.0) < 1e-8
        assert (v, u) not in frac
        node_load[u] += val
        node_load[v] += val
    assert all(load <= 1.0 + 1e-8 for load in node_load.values())


def test_initial_matching():
    """Test providing an initial matching."""
    G = nx.cycle_graph(4)
    
    # Create an initial matching (not optimal)
    initial = {(0, 1): 0.5, (1, 0): 0.5, (2, 3): 0.5, (3, 2): 0.5}
    
    # The algorithm should improve this to a perfect matching
    m = fractional_matching(G, initial_matching=initial)
    total_weight = sum(m.values())
    
    # Optimal solution should have total weight of 2
    assert abs(total_weight - 2) < 1e-8


@pytest.mark.parametrize(
    "n, p", [(30, 0.1), (50, 0.05)]  # Small enough for LP to solve in reasonable time
)
def test_compare_with_linear_programming(n, p):
    """
    Compare the fractional matching algorithm with a linear programming solution.
    The LP solution constrains values to {0, 0.5, 1} and should produce
    the same total weight as our specialized algorithm.
    """
    G = nx.fast_gnp_random_graph(n, p, seed=42)
    
    # Solve using the fractional_matching algorithm
    match = fractional_matching(G)
    algo_weight = sum(match.values())
    
    # Solve using linear programming
    lp_weight = solve_fractional_matching_lp(G)
    
    # The weights should be very close (allowing for small floating point differences)
    assert abs(algo_weight - lp_weight) < 1e-6, f"Algorithm: {algo_weight}, LP: {lp_weight}"


def solve_fractional_matching_lp(G):
    """
    Solve the fractional matching problem using linear programming.
    Constrains edge values to be in {0, 0.5, 1}.
    Returns the total weight of the maximum matching.
    """
    # Create the LP problem
    prob = pulp.LpProblem("FractionalMatching", pulp.LpMaximize)
    
    # Create a variable for each edge, constrained to {0, 0.5, 1}
    edges = list(G.edges())
    edge_vars = {}
    for u, v in edges:
        # Variables for each possible value (0, 0.5, 1)
        edge_vars[(u, v, 0)] = pulp.LpVariable(f"x_{u}_{v}_0", cat=pulp.LpBinary)
        edge_vars[(u, v, 0.5)] = pulp.LpVariable(f"x_{u}_{v}_0.5", cat=pulp.LpBinary)
        edge_vars[(u, v, 1)] = pulp.LpVariable(f"x_{u}_{v}_1", cat=pulp.LpBinary)
        
        # Each edge must have exactly one value assigned
        prob += edge_vars[(u, v, 0)] + edge_vars[(u, v, 0.5)] + edge_vars[(u, v, 1)] == 1
    
    # Objective: maximize the sum of edge values
    prob += pulp.lpSum([0.5 * edge_vars[(u, v, 0.5)] + 1 * edge_vars[(u, v, 1)] for u, v in edges])
    
    # Constraint: sum of incident edge values for each vertex must be ≤ 1
    for node in G.nodes():
        incident_edges = [(u, v) for u, v in edges if u == node or v == node]
        prob += pulp.lpSum([0.5 * edge_vars[(u, v, 0.5)] + 1 * edge_vars[(u, v, 1)] 
                            for u, v in incident_edges]) <= 1
    
    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Return zero if the problem was not solved
    if prob.status != pulp.LpStatusOptimal:
        return 0
    
    # Calculate the total weight
    total_weight = sum(0.5 * edge_vars[(u, v, 0.5)].value() + 1 * edge_vars[(u, v, 1)].value() 
                        for u, v in edges)
    
    return total_weight
